from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from friendship.models import Friendship
from friendship.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    FriendshipSerializerForCreate,
    FriendshipSerializerForDelete,
)
from friendship.api.pagination import FriendshipPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    pagination_class = FriendshipPagination


# 另一种方法是 /api/friendship/2?action=followers /api/friendship/2?action=following
#     def retrieve(self, request):
#         action = request.query_params.get('action','followers')
#         if action == 'followers':
#             ...

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        followers = Friendship.objects.filter(
            to_user_id=pk
        ).order_by('-created_at')
        page = self.paginate_queryset(followers)
        serializer = FollowerSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def following(self, request, pk):
        followings = Friendship.objects.filter(
            from_user_id=pk
        ).order_by('-created_at')
        page = self.paginate_queryset(followings)
        serializer = FollowingSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
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
    def unfollow(self, request, pk):
        self.get_object()
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

