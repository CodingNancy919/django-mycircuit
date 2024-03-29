from twitter.cache import USERPROFILE_PATTERN
from django.utils.cache import caches
from django.conf import settings
from accounts.models import UserProfile
from django.contrib.auth.models import User
from utils.memcached_helper import MemcachedHelper

cache = caches['default'] if settings.TESTING else caches['testing']


class UserProfileService(object):
    @classmethod
    def get_user_by_id(cls, user_id):
        return MemcachedHelper.get_object_from_cache(User, user_id)

    @classmethod
    def get_userprofile_from_cache(cls, user_id):
        key = USERPROFILE_PATTERN.format(user_id=user_id)
        # try to read from cache
        user_profile = cache.get(key)

        # cache hit
        if user_profile is not None:
            return user_profile
        # cache miss, read from db
        user_profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        cache.set(key, user_profile)
        return user_profile

    @classmethod
    def invalidate_userprofile_cache(cls, user_id):
        key = USERPROFILE_PATTERN.format(user_id=user_id)
        cache.delete(key)

