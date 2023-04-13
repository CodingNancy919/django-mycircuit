from newsfeeds.api.serializer import NewsFeedSerializer
from rest_framework import viewsets
from newsfeeds.models import NewsFeed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from utils.paginations import EndlessPagination
from newsfeeds.service import NewsFeedService


class NewsFeedViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = EndlessPagination

    def get_query_set(self):
        # 当前查看newsfeed是有权限的，只能查看当前登录用户的newsfeed
        # 也可以写成如下
        # self.request.user.user_newsfeed_set().all()
        return NewsFeed.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def list(self, request):
        user_id = request.user.id
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(user_id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            queryset = NewsFeed.objects.filter(
                user_id=user_id
                ).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = NewsFeedSerializer(page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)
