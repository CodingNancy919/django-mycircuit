from rest_framework import serializers
from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendship.models import Friendship
from rest_framework import exceptions
from friendship.services import FriendshipService
from accounts.services import UserProfileService

# python支持动态生成和加载变量，类似于对哈希表进行操作，可以定义一个object level的缓存变量，java则需要预先定义
# 每次web server访问cache的时候，_cached_following_user_id是存在本地进程的内存中 http request结束以后被释放


class BaseFriendshipSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField()
    has_followed = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    def get_user_id(self, obj):
        raise NotImplementedError

    def get_user(self, obj):
        user = UserProfileService.get_user_by_id(self.get_user_id(obj))
        return UserSerializerForFriendship(user).data

    def get_has_followed(self, obj):
        return self.get_user_id(obj) in self.following_user_id_set

    def get_created_at(self, obj):
        return obj.created_at

    @property
    def following_user_id_set(self):
        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, "_cached_following_user_id_set"):
            return getattr(self, "_cached_following_user_id_set")

        following_user_id_set = FriendshipService.get_following_user_id_set(
            from_user_id=self.context['request'].user.id)
        setattr(self, "_cached_following_user_id_set", following_user_id_set)
        return getattr(self, "_cached_following_user_id_set")


# class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
#     # 也可以写作： from_user = UserSerializerForFriendship()
#     user = UserSerializerForFriendship(source='cached_from_user')
#     has_followed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Friendship
#         fields = ['user', 'created_at', 'has_followed']
#
#     def get_user_id(self, obj):
#         return
#     def get_has_followed(self, obj):
#         if self.context['request'].user.is_anonymous:
#             return False
#         # 关注我的人是否在我的关注列表里
#         return obj.from_user_id in self.following_user_id_set
#

class FollowerSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.from_user_id
#
# class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
#     user = UserSerializerForFriendship(source='cached_to_user')
#     has_followed = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Friendship
#         fields = ['user', 'created_at', 'has_followed']
#
#     def get_has_followed(self, obj):
#         if self.context['request'].user.is_anonymous:
#             return False
#         return obj.to_user_id in self.following_user_id_set


class FollowingSerializer(BaseFriendshipSerializer):
    def get_user_id(self, obj):
        return obj.to_user_id


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
