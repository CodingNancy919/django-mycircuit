from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.services import LikeService
from likes.api.serializers import LikeSerializer
from tweets.constant import TWEET_PHOTOS_UPLOAD_LIMIT
from rest_framework.exceptions import ValidationError
from tweets.services import TweetService
from utils.redis_helper import RedisHelper


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet(source="cached_user")
    has_liked = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()


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
            'photo_urls',
        )

    def get_comments_count(self, obj):
        return RedisHelper.get_count(obj, "comments_count")

    def get_likes_count(self, obj):
        return RedisHelper.get_count(obj, "likes_count")

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_photo_urls(self, obj):
        photo_urls = []
        for photo in obj.tweetphoto_set.all().order_by('order'):
            photo_urls.append(photo.file.url)
        return photo_urls


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
            'photo_urls',
        )

    # def get_comments(self, obj):
    #     return CommentSerializer(obj.comment_set.all(), many=True).data


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Tweet
        fields = ('content', 'files')

    def validate(self, data):
        if len(data.get('files', [])) > TWEET_PHOTOS_UPLOAD_LIMIT:
            raise ValidationError({
                'message': f'You can upload {TWEET_PHOTOS_UPLOAD_LIMIT} at most'
            })
        return data

    def create(self, validated_data):
        content = validated_data['content']
        user = self.context['request'].user
        tweet = Tweet.objects.create(
            user=user,
            content=content,
        )
        files = validated_data.get('files')
        if files:
            TweetService.create_photos_from_files(tweet, files)
        return tweet
