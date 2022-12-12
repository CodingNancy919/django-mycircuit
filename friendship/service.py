from friendship.models import Friendship
from django.contrib.auth.models import User


class FriendshipService(object):
    @classmethod
    def get_all_followers(cls, user):
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)
        # return followers
        friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]
