from newsfeeds.models import NewsFeed
from testing.testcase import TestCase
from utils.redis_client import RedisClient
from newsfeeds.service import NewsFeedService
from twitter.cache import USER_NEWSFEEDS_PATTERN
from newsfeeds.tasks import fanout_newsfeed_main_task


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.user2 = self.create_user(username='user2')
        self.clear_cache()

    def test_get_user_newsfeeds(self):
        RedisClient.clear()
        conn = RedisClient.get_connection()

        newsfeeds_id = []

        for i in range(3):
            tweet = self.create_tweet(self.user1, content='tweet {}'.format(i))
            newsfeed = self.create_newsfeed(self.user2, tweet)
            newsfeeds_id.append(newsfeed.id)

        newsfeeds_id = newsfeeds_id[::-1]

        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual([item.id for item in cached_newsfeeds], newsfeeds_id)

        new_tweet = self.create_tweet(self.user1, content='new tweet')
        new_newsfeed = self.create_newsfeed(self.user2, new_tweet)
        newsfeeds_id.insert(0, new_newsfeed.id)
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual([item.id for item in cached_newsfeeds], newsfeeds_id)

    def test_create_new_newsfeed_before_get_cached_newsfeeds(self):
        tweet = self.create_tweet(self.user1, content='tweet 1')
        newsfeed = self.create_newsfeed(self.user2, tweet)

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.user2.id)
        self.assertEqual(conn.exists(key), False)
        tweet2 = self.create_tweet(self.user1, content='tweet 2')
        newsfeed2 = self.create_newsfeed(self.user2, tweet2)
        self.assertEqual(conn.exists(key), True)

        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual([item.id for item in cached_newsfeeds], [newsfeed2.id, newsfeed.id])

class NewsFeedTasksTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.user2 = self.create_user(username='user2')
        self.clear_cache()

    def test_fanout_newsfeeds(self):
        # 正常 request

        tweet = self.create_tweet(self.user2, "tweet 1")
        self.create_friendship(self.user1, self.user2)
        msg = fanout_newsfeed_main_task(tweet.id)
        self.assertEqual(msg, "1 newsfeeds are going to be fanout, 1 batched are created")
        self.assertEqual(2, NewsFeed.objects.count())
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(1, len(cached_newsfeeds))

        for i in range(2):
            user = self.create_user(username="follower {}".format(i+1))
            self.create_friendship(user, self.user2)
        tweet = self.create_tweet(self.user2, "tweet 2")
        msg = fanout_newsfeed_main_task(tweet.id)
        self.assertEqual(msg, "3 newsfeeds are going to be fanout, 1 batched are created")
        self.assertEqual(6, NewsFeed.objects.count())
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(2, len(cached_newsfeeds))

        tweet = self.create_tweet(self.user2, "tweet 3")
        self.create_friendship(self.create_user(username="new user"), self.user2)
        msg = fanout_newsfeed_main_task(tweet.id)
        self.assertEqual(msg, "4 newsfeeds are going to be fanout, 1 batched are created")
        self.assertEqual(11, NewsFeed.objects.count())
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(3, len(cached_newsfeeds))
        cached_newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(3, len(cached_newsfeeds))







