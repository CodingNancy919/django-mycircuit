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


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        followers = Friendship.objects.filter(
            to_user_id=pk
        ).order_by('-created_at')
        serializer = FollowerSerializer(followers, many=True)
        return Response({'followers': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def following(self, request, pk):
        followings = Friendship.objects.filter(
            from_user_id=pk
        ).order_by('-created_at')
        serializer = FollowingSerializer(followings, many=True)
        return Response({'followings': serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # pk 对应url api/friendship/id/follow的id
        # 从queryset中查询pk如果不存在返回404
        self.get_object()

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk
        })
        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        friendship = serializer.save()
        return Response({
            'Success': True,
            'Your friend info': FollowingSerializer(friendship).data
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

