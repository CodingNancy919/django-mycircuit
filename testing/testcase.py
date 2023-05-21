
from comments.models import Comment
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from django.utils.cache import caches
from friendship.models import Friendship
from likes.models import Like
from newsfeeds.models import NewsFeed
from rest_framework.test import APIClient
from tweets.models import Tweet
from utils.redis_client import RedisClient
from django_hbase.models import HBaseModel
from friendship.services import FriendshipService
from gatekeeper.models import GateKeeper


class TestCase(DjangoTestCase):
    hbase_tables_created = False

    def setUp(self):
        self.clear_cache()
        self.hbase_tables_created = True
        try:
            for hbase_model_class in HBaseModel.__subclasses__():
                hbase_model_class.create_table()
        except Exception:
            self.tear_down()
            raise

    def tear_down(self):
        if not self.hbase_tables_created:
            return
        for hbase_model_class in HBaseModel.__subclasses__():
            hbase_model_class.drop_table()

    # def test_happybase(self):
    #     from django.conf import settings
    #     import happybase
    #     conn = happybase.Connection("192.168.33.10")
    #     conn.tables()

    def clear_cache(self):
        caches['testing'].clear()
        RedisClient.clear()

    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = '{}@jiuzhang.com'.format(username)
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_friendship(self, from_user, to_user):
        return FriendshipService.follow(from_user_id=from_user.id, to_user_id=to_user.id)

    def create_newsfeed(self, user, tweet):
        return NewsFeed.objects.create(user=user, tweet=tweet)

    def create_comment(self, user, tweet, comment=None):
        if comment is None:
            comment = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, comment=comment)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            user=user,
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.force_authenticate(user)
        return user, client



