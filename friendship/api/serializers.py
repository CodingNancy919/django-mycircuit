from rest_framework import serializers
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendship.models import Friendship
from rest_framework import exceptions


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    class Meta:
        model = Friendship
        fields = ['user', 'created_at']


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
