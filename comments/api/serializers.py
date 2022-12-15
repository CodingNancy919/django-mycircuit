from rest_framework import serializers
from comments.models import Comment
from tweets.models import Tweet
from rest_framework import exceptions
from accounts.api.serializers import UserSerializerForComment


class CommentSerializerForCreate(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    tweet_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = (
            'user_id',
            'tweet_id',
            'comment',
        )

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise exceptions.ValidationError({
                'message': 'The tweet does not exist'
            })
        return data

    def create(self, validated_data):
        tweet_id = validated_data['tweet_id']
        user_id = validated_data['user_id']
        content = validated_data['comment']
        comment = Comment.objects.create(tweet_id=tweet_id, user_id=user_id, comment=content)
        return comment


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'tweet_id',
            'comment',
            'created_at',
            'updated_at',
        )
