from rest_framework import viewsets
from utils.decorators import required_params
from tweets.models import Tweet
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from rest_framework.response import Response
from newsfeeds.service import NewsFeedService
from utils.paginations import EndlessPagination
from tweets.services import TweetService


# 这里正常不用ModelViewSet因为它支持增删查改
class TweetViewSet(viewsets.GenericViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate
    pagination_class = EndlessPagination

    # 这里的action指的就是list create等函数
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id'])
    def list(self, request):
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)
        # tweets = Tweet.objects.filter(
        #     user_id=user_id
        # ).order_by('-created_at')
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).prefetch_related('user')
        cached_tweets = TweetService.get_cached_tweets(user_id)
        page = self.paginator.paginate_cached_list(cached_tweets, request)
        if page is None:
            # 这句查询会被翻译为
            # select * from twitter_tweets
            # where user_id = xxx
            # order by created_at desc
            # 这句 SQL 查询会用到 user 和 created_at 的联合索引
            # 单纯的 user 索引是不够的
            queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
            page = self.paginate_queryset(queryset)
        serializer = TweetSerializer(
            page,
            context={'request': request},
            many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        serializer = TweetSerializerForCreate(
            context={'request': request},
            data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet,  context={'request': request}).data, status=201)
