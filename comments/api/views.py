from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner
from utils.decorators import required_params


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
    serializer_class = CommentSerializerForCreate
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        # 注意要加用 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是 AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # if 'tweet_id' not in request.query_params:
        #     return Response({
        #         'Success': False,
        #         'message': "missing tweet_id in request",
        #     }, status=status.HTTP_400_BAD_REQUEST)
        # 使用prefetch_related可以减少DB的查询, selected_related会导致join查询
        comments = Comment.objects.filter(tweet_id=request.query_params['tweet_id'])\
            .prefetch_related('user')\
            .order_by('created_at')
        # queryset = self.get_queryset()
        # comments = self.filter_queryset(queryset)\
        #     .prefetch_related('user')\
        #     .order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response({
            'comments': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = {
             'user_id': request.user.id,
             'tweet_id': request.data.get('tweet_id'),
             'comment': request.data.get('comment'),
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

    def update(self, request, *args, **kwargs):
        # get_object 是 DRF 包装的对于detail=True的action一个函数，会在找不到的时候 raise 404 error
        # 所以这里无需做额外判断
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'Success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save 方法会触发 serializer 里的 update 方法，点进 save 的具体实现里可以看到
        # save 是根据 instance 参数有没有传来决定是触发 create 还是 update
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # DRF 里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        comment = self.get_object()
        comment.delete()
        return Response({'Success': True}, status=status.HTTP_200_OK)



