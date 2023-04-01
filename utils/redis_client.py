import redis
from django.conf import settings


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # 使用singleton模式 全局只创建一个connection
        if cls.conn is not None:
            return cls.conn
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        if not settings.TESTING:
            raise Exception("can't flush redis in production environment")
        conn = cls.get_connection()
        conn.flushdb()
