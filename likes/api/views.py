from likes.models import Like
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
    LikeSerializerForCancel,
)
from utils.decorators import required_params
from rest_framework.response import Response
from rest_framework.decorators import action
from inbox.services import NotificationService


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(method='POST', params=['content_type', 'object_id'])
    def create(self, request):
        serializer = LikeSerializerForCreate(
            context={'request': request},
            data=request.data
        )
        if not serializer.is_valid():
            return Response({
                "Success": False,
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        like, created = serializer.get_or_create()
        if created:
            NotificationService.send_like_notifications(like)
        return Response({
                "Success": True,
                "message": LikeSerializer(like).data,
            }, status=status.HTTP_201_CREATED)

    @action(methods=["POST"], detail=False)
    @required_params(method='POST', params=['content_type', 'object_id'])
    def cancel(self, request):
        # 这里也可以采用 delete /api/likes/的方法，但是前端需要获取object的id或instance才能发送请求，可能来不及，
        # 所以还是采用/api/likes/cancel
        serializer = LikeSerializerForCancel(
            context={'request': request},
            data=request.data
        )
        if not serializer.is_valid():
            return Response({
                "Success": False,
                "message": "Please check your input",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = serializer.cancel()
        return Response({
            "Success": True,
            "deleted": deleted,
        }, status=status.HTTP_200_OK)





