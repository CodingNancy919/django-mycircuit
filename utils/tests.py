from utils.redis_client import RedisClient
from testing.testcase import TestCase
from utils.redis_serializer import DjangoModelSerializer


class RedisClientTests(TestCase):
    def setUp(self):
        super(RedisClientTests, self).setUp()
        self.user1 = self.create_user(username='user1')
        self.tweet = self.create_tweet(self.user1)

    def test_redis_client(self):
        conn = RedisClient.get_connection()
        conn.lpush('redis_key', 1)
        conn.lpush('redis_key', 2)
        cached_list = conn.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        RedisClient.clear()
        cached_list = conn.lrange('redis_key', 0, -1)
        self.assertEqual(cached_list, [])

    def test_tweet_redis(self):
        self.tweet = self.create_tweet(self.user1)
        conn = RedisClient.get_connection()
        serialized_tweet = DjangoModelSerializer.serialize(self.tweet)
        conn.set(f'tweet {self.tweet.id}', serialized_tweet)

        data = conn.get(f'tweet notExist')
        self.assertEqual(data, None)

        serialized_tweet = conn.get(f'tweet {self.tweet.id}')
        self.assertEqual(self.tweet, DjangoModelSerializer.deserialize(serialized_tweet))
