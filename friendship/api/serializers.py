from rest_framework import serializers
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendship.models import Friendship
from rest_framework import exceptions
from friendship.service import FriendshipService


class FollowerSerializer(serializers.ModelSerializer):
    # 也可以写作： from_user = UserSerializerForFriendship()
    user = UserSerializerForFriendship(source='from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.from_user)


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ['user', 'created_at', 'has_followed']

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(self.context['request'].user, obj.to_user)


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ['from_user_id', 'to_user_id', 'created_at']


    def validate(self, data):
        from_user = data['from_user_id']
        to_user = data['to_user_id']
        if from_user == to_user:
            raise exceptions.ValidationError({
                'message': 'You can not follow yourself.'
            })

        if not User.objects.filter(id=to_user).exists():
            raise exceptions.ValidationError({
                'message': 'The user you want to follow does not exist'
            })
        # if Friendship.objects.filter(from_user_id=from_user, to_user_id=to_user).exists():
        #     raise exceptions.ValidationError({
        #         'message': 'You have already followed this user'
        #     })
        return data

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']

        friendship = Friendship.objects.create(from_user_id=from_user_id, to_user_id=to_user_id)
        return friendship


class FriendshipSerializerForDelete(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ['from_user_id', 'to_user_id', 'created_at']

    def validate(self, data):
        from_user = data['from_user_id']
        to_user = data['to_user_id']
        if from_user == to_user:
            raise exceptions.ValidationError({
                'message': 'You can not unfollow yourself.'
            })
        if not Friendship.objects.filter(
                from_user_id=from_user,
                to_user_id=to_user
        ).exists():
            raise exceptions.ValidationError({
                'message': 'You can not unfollow a person who is not your friend.'
            })
        return data
