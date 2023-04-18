from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from friendship.models import Friendship
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from friendship.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
    FriendshipSerializerForDelete,
)
from friendship.api.pagination import FriendshipPagination
from friendship.services import FriendshipService


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk=1) 查询一下这个 object 在不在
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # 一般来说，不同的 views 所需要的 pagination 规则肯定是不同的，因此一般都需要自定义
    pagination_class = FriendshipPagination


# 另一种方法是 /api/friendship/2?action=followers /api/friendship/2?action=following
#     def retrieve(self, request):
#         action = request.query_params.get('action','followers')
#         if action == 'followers':
#             ...

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def followers(self, request, pk):
        followers = Friendship.objects.filter(
            to_user_id=pk
        ).order_by('-created_at')
        page = self.paginate_queryset(followers)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    @method_decorator(ratelimit(key='user_or_ip', rate='3/s', method='GET', block=True))
    def following(self, request, pk):
        followings = Friendship.objects.filter(
            from_user_id=pk
        ).order_by('-created_at')
        page = self.paginate_queryset(followings)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def follow(self, request, pk):
        # pk 对应url api/friendship/id/follow的id detail=True会自动执行self.get_object()
        # 从queryset.filter(pk=id)中查询pk在不在 如果不存在返回404
        self.get_object()

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk
        })
        # 特殊判断重复 follow 的情况（比如前端猛点好多少次 follow)
        # 静默处理，不报错，因为这类重复操作因为网络延迟的原因会比较多，没必要当做错误处理
        if Friendship.objects.filter(from_user_id=request.user.id, to_user_id=pk).exists():
            return Response({
                'Success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        friendship = serializer.save()

        return Response({
            'Success': True,
            'Your friend info': FollowingSerializer(friendship, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    @method_decorator(ratelimit(key='user', rate='10/s', method='POST', block=True))
    def unfollow(self, request, pk):
        self.get_object()
        # 注意 pk 的类型是 str，所以要做类型转换
        # if request.user.id == int(pk):
        #     return Response({
        #         'success': False,
        #         'message': 'You cannot unfollow yourself',
        #     }, status=status.HTTP_400_BAD_REQUEST)
        serializer = FriendshipSerializerForDelete(data={
            'from_user_id': request.user.id,
            'to_user_id': pk
        })
        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = Friendship.objects.filter(
            from_user_id=request.user.id,
            to_user_id=pk
        ).delete()

        return Response(data={'Success': True, 'deleted': deleted})

    def list(self, request):
        return Response({'message': 'this is a friendship home page'})

