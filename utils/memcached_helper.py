from django.utils.cache import caches
from django.conf import settings


cache = caches['default'] if settings.TESTING else caches['testing']


class MemcachedHelper(object):

    @classmethod
    def get_key(cls, model_class, object_id):
        return "{}:{}".format(model_class.__name__, object_id)

    @classmethod
    def get_object_from_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)

        # try to read from cache
        object = cache.get(key)

        # cache hit
        if object is not None:
            return object
        # cache miss, read from db
        object = model_class.objects.filter(id=object_id)
        cache.set(key, object)
        return object

    @classmethod
    def invalidate_object_cache(cls, model_class, object_id):
        key = cls.get_key(model_class, object_id)
        cache.delete(key)
