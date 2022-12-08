from rest_framework import viewsets
from rest_framework.decorators import action
from tweets.models import Tweet
from rest_framework.permissions import IsAuthenticated, AllowAny
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from rest_framework.response import Response


# 这里正常不用ModelViewSet因为它支持增删查改
class TweetViewSet(viewsets.GenericViewSet):
    # queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    # 这里的action指的就是list create等函数
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
        serializer = TweetSerializer(tweets, many=True)
        return Response({'tweets': serializer.data})

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
        return Response(TweetSerializer(tweet).data, status=201)
