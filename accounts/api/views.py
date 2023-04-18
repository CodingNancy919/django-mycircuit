from accounts.api.serializers import UserSerializer
from django.contrib.auth.models import User
from accounts.models import UserProfile
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework import status
from utils.permissions import IsObjectOwner
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from accounts.api.serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    UserSerializerWithProfile,
    UserProfileSerializerForUpdate,
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    ReadOnlyModelViewSet(can't edit user) ModelViewSet
    serializer_class用来渲染表单
    permission_classes检测用户是否登录
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    permission_classes = (permissions.IsAdminUser,)


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    serializer_class = UserProfileSerializerForUpdate
    permission_classes = (IsObjectOwner,)


class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def login(self, request):
        """
        default username is admin, password is admin
        request.user is a User object stored in request, just like session and data
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exists",
            }, status=status.HTTP_400_BAD_REQUEST)
        """
           create session key and hash for the user
           and return the user
        """
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=status.HTTP_400_BAD_REQUEST)
        """
        set the session key and user object in the request, browser will store the token in cookie
        """
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(context={'request': request}, instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def logout(self, request):
        """
        登出当前用户
        flush session and reset user to anonymous user in request
        """
        django_logout(request)
        return Response({"success": True})

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate='3/s', method='POST', block=True))
    def signup(self, request):
        """
        使用 username, email, password 进行注册
        """
        # 不太优雅的写法
        # username = request.data.get('username')
        # if not username:
        #     return Response("username required", status=400)
        # password = request.data.get('password')
        # if not password:
        #     return Response("password required", status=400)
        # if User.objects.filter(username=username).exists():
        #     return Response("password required", status=400)
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        # Create UserProfile object
        user.profile
        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(context={'request': request}, instance=user).data,
        }, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        查看用户当前的登录状态和具体信息
        """
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(context={'request': request}, instance=request.user).data
        return Response(data)
