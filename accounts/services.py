from twitter.cache import USER_PATTERN, USERPROFILE_PATTERN
from django.contrib.auth.models import User
from django.utils.cache import caches
from django.conf import settings
from accounts.models import UserProfile

cache = caches['default'] if settings.TESTING else caches['testing']


class UserService(object):
    @classmethod
    def get_user_from_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)

        # try to read from cache
        user = cache.get(key)

        # cache hit
        if user is not None:
            return user
        # cache miss, read from db
        try:
            user = User.objects.filter(id=user_id)
            cache.set(key, user)
        except User.DoesNotExist:
            user = None
        cache.set(key, user)
        return user

    @classmethod
    def invalidate_user_cache(cls, user_id):
        key = USER_PATTERN.format(user_id=user_id)
        cache.delete(key)


class UserProfileService(object):
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

