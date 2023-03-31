from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from accounts.listeners import user_changed, userprofile_changed
from accounts.services import UserProfileService


class UserProfile(models.Model):
    # One2One field 会创建一个 unique index，确保不会有多个 UserProfile 指向同一个 User
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    # Django 还有一个 ImageField，但是尽量不要用，会有很多的其他问题，用 FileField 可以起到
    # 同样的效果。因为最后我们都是以文件形式存储起来，使用的是文件的 url 进行访问
    avatar = models.FileField(null=True)
    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        pass

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)

    # 定义一个 profile 的 property 方法，植入到 User 这个 model 里
    # 这样当我们通过 user 的一个实例化对象访问 profile 的时候，即 user_instance.profile
    # 就会在 UserProfile 中进行 get_or_create 来获得对应的 profile 的 object
    # 这种写法实际上是一个利用 Python 的灵活性进行 hack 的方法，这样会方便我们通过 user 快速
    # 访问到对应的 profile 信息。
    def get_profile(user):
        if hasattr(user, '_cached_user_profile'):
            return getattr(user, '_cached_user_profile')
        user_profile = UserProfileService.get_userprofile_from_cache(user_id=user.id)
        setattr(user, '_cached_user_profile', user_profile)
        return getattr(user, '_cached_user_profile')

    # 给 User Model 增加了一个 profile 的 property 方法用于快捷访问,instance level cache
    # 相当于在User model里植入 @property def get_profile(user):
    User.profile = property(get_profile)

# hook up with listeners to invalidate cache


pre_delete.connect(user_changed, sender=User)
post_save.connect(user_changed, sender=User)
pre_delete.connect(userprofile_changed, sender=UserProfile)
post_save.connect(userprofile_changed, sender=UserProfile)
