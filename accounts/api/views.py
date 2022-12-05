from rest_framework import views, permissions
from rest_framework import viewsets
from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializer, LoginSerializer, SignupSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        """
        request.user is a User object stored in request, just like session and data
        """
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """
        flush session and reset user to anonymous user in request
        """
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        queryset = User.objects.filter(username=username)
        # print(queryset.query)
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exists",
            }, status=400)
        """
        create session key and hash for the user
        and return the user
        """
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match",
            }, status=400)

        """
        set the session key and user object in the request, browser will store the token in cookie
        """
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(user).data
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        user = serializer.save()
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(user).data
        }, status=201)


