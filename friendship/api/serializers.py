from rest_framework import serializers
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendship.models import Friendship


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

# class FriendshipSerializer(serializers.ModelSerializer):