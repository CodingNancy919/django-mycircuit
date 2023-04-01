from utils.time_helpers import utc_now
from testing.testcase import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from tweets.models import TweetPhoto
from tweets.constant import TweetPhotoStatus
from utils.redis_client import RedisClient
from utils.redis_serializer import DjangoModelSerializer
from tweets.services import TweetService
from twitter.cache import USER_TWEETS_PATTERN
LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'


# 类名用大坨峰写法命名
class TweetTest(TestCase):
    # 函数名用蛇形sneak style写法命名
    def test_hours_to_now(self):
        user = User.objects.create_user(username='Nancy')
        tweet = Tweet.objects.create(user=user, content='This is only a test')
        tweet.created_at = utc_now() - timedelta(hours=10)
        tweet.save()
        self.assertEqual(tweet.hours_to_now, 10)

    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.tweet = self.create_tweet(self.user1)

    def test_tweet_photo(self):
        tweet_photo = TweetPhoto.objects.create(
            tweet=self.tweet,
            user=self.user1,
        )

        self.assertEqual(tweet_photo.user, self.user1)
        self.assertEqual(tweet_photo.tweet.id, self.tweet.id)
        self.assertEqual(tweet_photo.status, TweetPhotoStatus.PENDING)
        self.assertEqual(tweet_photo.has_deleted, False)

    def test_tweet_redis(self):
        self.tweet = self.create_tweet(self.user1)
        conn = RedisClient.get_connection()
        serialized_tweet = DjangoModelSerializer.serialize(self.tweet)
        conn.set(f'tweet {self.tweet.id}', serialized_tweet)

        data = conn.get(f'tweet notExist')
        self.assertEqual(data, None)

        serialized_tweet = conn.get(f'tweet {self.tweet.id}')
        self.assertEqual(self.tweet, DjangoModelSerializer.deserialize(serialized_tweet))


class TweetServiceTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.clear_cache()

    def test_get_user_tweets(self):
        RedisClient.clear()
        conn = RedisClient.get_connection()

        tweets_id = []
        for i in range(3):
            tweet = self.create_tweet(self.user1, content='tweet {}'.format(i))
            tweets_id.append(tweet.id)

        tweets_id = tweets_id[::-1]

        cached_tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([item.id for item in cached_tweets], tweets_id)

        new_tweet = self.create_tweet(self.user1, content='new tweet')
        tweets_id.insert(0, new_tweet.id)
        cached_tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([item.id for item in cached_tweets], tweets_id)

    def test_create_new_tweet_before_get_cached_tweets(self):
        tweet1 = self.create_tweet(self.user1, content='tweet 1')

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_TWEETS_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), False)
        tweet2 = self.create_tweet(self.user1, content='tweet 2')
        self.assertEqual(conn.exists(key), True)

        cached_tweets = TweetService.get_cached_tweets(self.user1.id)
        self.assertEqual([item.id for item in cached_tweets], [tweet2.id, tweet1.id])














