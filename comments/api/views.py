from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from comments.models import Comment
from comments.api.serializers import CommentSerializer, CommentSerializerForCreate
from django.contrib.auth.models import User


class CommentViewSet(viewsets.GenericViewSet):
    # GenericViewSet 只实现list create update destroy方法 不实现retrieve
    # 用 get_permissions可以统一处理不同methods的权限，或者在action修饰符中用permission_classes来定义
    # POST /api/comments/   create
    # GET  /api/comments/   list
    # GET  /api/comments/1  retrieve
    # PUT  /api/comments/1  update
    # PATCH  /api/comments/1  partial_update
    # DELETE  /api/comments/1  destroy
    queryset = Comment.objects.all()
    serializer_class = CommentSerializerForCreate()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
             'user_id': request.user.id,
             'tweet_id': request.data.get('tweet_id'),
             'comment': request.data.get('content'),
         }
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )





