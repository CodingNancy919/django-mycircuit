from utils.redis_client import RedisClient
from utils.redis_serializer import DjangoModelSerializer
from django.conf import settings


class RedisHelper:
    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()
        serialized_list = []
        # 最多只 cache REDIS_LIST_LENGTH_LIMIT 那么多个 objects
        # 超过这个限制的 objects，就去数据库里读取。一般这个限制会比较大，比如 1000
        # 因此翻页翻到 1000 的用户访问量会比较少，从数据库读取也不是大问题
        for object in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:
            serialized_data = DjangoModelSerializer.serialize(object)
            serialized_list.append(serialized_data)
        if serialized_list:
            # 加*的作用是把[1,2,3,4,5,6]转换成1,2,3,4,5,6 把list扩展开
            # 注意此处不要用N+1 query 可以使用rpush一次插入
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def get_objects(cls, key, queryset):
        conn = RedisClient.get_connection()
        # 如果在 cache 里存在，则直接拿出来，然后返回
        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1)
            objects = []
            for serialized_tweet in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_tweet)
                objects.append(deserialized_obj)
            return objects
        cls._load_objects_to_cache(key, queryset)

        # 转换为 list 的原因是保持返回类型的统一，因为存在 redis 里的数据是 list 的形式
        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()

        if conn.exists(key):
            serialized_data = DjangoModelSerializer.serialize(obj)
            conn.lpush(key, serialized_data)
            conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT-1)
            return

        # 如果 key 不存在，直接从数据库里 load
        # 就不走单个 push 的方式加到 cache 里了
        cls._load_objects_to_cache(key, queryset)

    @classmethod
    def get_obj_key(cls, obj, attr):
        key = "{}{}{}".format(obj.__class__.__name__, obj.object_id, attr)
        return key

    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_obj_key(obj, attr)
        if not conn.exists(key):
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.incr(key)

    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_obj_key(obj, attr)
        if not conn.exists(key):
            conn.set(key, getattr(obj, attr))
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
            return getattr(obj, attr)
        return conn.decr(key)

    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_obj_key(obj, attr)
        count = conn.get(key)
        if count is not None:
            return int(count)

        obj.refresh_from_db()
        count = getattr(obj, attr)
        conn.set(key, count)
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return count

















