from utils.redis_client import RedisClient
from testing.testcase import TestCase


class RedisClientTests(TestCase):
    def setUp(self):
        RedisClient.clear()

    def test_redis_client(self):
        conn = RedisClient.get_connection()
        conn.lpush('redis_key', 1)
        conn.lpush('redis_key', 2)
        cached_list = conn.lrange(self, 'redis_key', 0, -1)
        self.assertEqual(cached_list, [b'2', b'1'])

        RedisClient.clear()
        cached_list = conn.lrange(self, 'redis_key', 0, -1)
        self.assertEqual(cached_list, [])
