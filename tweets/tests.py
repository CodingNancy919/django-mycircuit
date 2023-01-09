from utils.time_helpers import utc_now
from testing.testcase import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from tweets.models import TweetPhoto
from tweets.constant import TweetPhotoStatus
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


