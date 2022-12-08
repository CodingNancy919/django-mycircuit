from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from friendship.models import Friendship
from friendship.api.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    # FriendshipSerializer
)


class FriendshipViewSet(viewsets.GenericViewSet):

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        followers = Friendship.objects.filter(
            to_user_id=pk
        ).order_by('-created_at')
        serializer = FollowerSerializer(followers, many=True)
        return Response(
            {'followers': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def following(self, request, pk):
        followings = Friendship.objects.filter(
            from_user_id=pk
        ).order_by('-created_at')
        serializer = FollowingSerializer(followings, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request):
        pass

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request):
        pass

    def list(self, request):
        return Response({'message': 'this is a friendship home page'})

