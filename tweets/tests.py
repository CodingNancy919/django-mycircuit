from utils.time_helpers import utc_now
from django.test import TestCase
from django.contrib.auth.models import User
from tweets.models import Tweet
from datetime import timedelta
from rest_framework.test import APIClient
from django.contrib.auth.models import User


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

