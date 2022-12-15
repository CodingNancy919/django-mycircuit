from newsfeeds.api.serializer import NewsFeedSerializer
from rest_framework import viewsets
from newsfeeds.models import NewsFeed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_query_set(self):
        # 当前查看newsfeed是有权限的，只能查看当前登录用户的newsfeed
        # 也可以写成如下
        # self.request.user.user_newsfeed_set().all()
        return NewsFeed.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def list(self, request):
        serializer = NewsFeedSerializer(self.get_query_set(), many=True)
        return Response({'newsfeeds': serializer.data}, status=status.HTTP_200_OK)
