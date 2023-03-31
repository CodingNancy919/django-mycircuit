from rest_framework import serializers
from newsfeeds.models import NewsFeed
from accounts.api.serializers import UserSerializerForTweet
from tweets.api.serializers import TweetSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    # newsfeed is for user, no need to show details of the user himself
    # user = UserSerializerForTweet()
    tweet = TweetSerializer()

    class Meta:
        model = NewsFeed
        fields = ['id', 'tweet', 'created_at']