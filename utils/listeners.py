
def object_changed(sender, instance, **kwags):
    from utils.memcached_helper import MemcachedHelper
    MemcachedHelper.invalidate_object_cache(sender, instance.id)

