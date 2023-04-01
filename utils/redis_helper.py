from utils.redis_client import RedisClient
from utils.redis_serializer import DjangoModelSerializer
from django.conf import settings


class RedisHelper:
    @classmethod
    def _load_objects_to_cache(cls, key, objects):
        conn = RedisClient.get_connection()
        serialized_list = []
        for object in objects:
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
            serialized_list = conn.lrange(key, -1, 0)
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
            return

        # 如果 key 不存在，直接从数据库里 load
        # 就不走单个 push 的方式加到 cache 里了
        cls._load_objects_to_cache(key, queryset)






