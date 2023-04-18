from newsfeeds.api.serializer import NewsFeedSerializer
from rest_framework import viewsets
from newsfeeds.models import NewsFeed
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from utils.paginations import EndlessPagination
from newsfeeds.service import NewsFeedService
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit


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

    @method_decorator(ratelimit(key='user', rate='5/s', method='GET', block=True))
    def list(self, request):
        # newsfeeds = NewsFeedService.get_cached_newsfeeds(request.user.id)
        # page = self.paginate_queryset(newsfeeds)
        user_id = request.user.id
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(user_id)
        page = self.paginator.paginate_cached_list(cached_newsfeeds, request)
        if page is None:
            queryset = NewsFeed.objects.filter(
                user_id=user_id
                ).order_by('-created_at')
            page = self.paginator.paginate_queryset(queryset, request)
        serializer = NewsFeedSerializer(page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)
