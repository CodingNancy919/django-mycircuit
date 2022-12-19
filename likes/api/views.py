from likes.models import Like
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from likes.api.serializers import (
    LikeSerializer,
    LikeSerializerForCreate,
)
from utils.decorators import required_params
from rest_framework.response import Response


class LikeViewSet(viewsets.GenericViewSet):
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializerForCreate

    @required_params(required_attr='data', params=['content_type', 'object_id'])
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

        like = serializer.save()
        return Response({
                "Success": True,
                "message": LikeSerializer(like).data,
            }, status=status.HTTP_201_CREATED)





