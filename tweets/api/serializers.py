from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.services import LikeService
from likes.api.serializers import LikeSerializer


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet()
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'has_liked',
            'comments_count',
            'likes_count',
        )

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)


class TweetSerializerForDetail(TweetSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)
    # 使用serializers.SerializerMethodField实现comments
    # comments = serializers.SerializerMethodField()
    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments',
            'likes',
            'has_liked',
            'comments_count',
            'likes_count',
        )

    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        content = validated_data['content']
        user = self.context['request'].user
        tweet = Tweet.objects.create(
            user=user,
            content=content,
        )
        return tweet
