from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete, post_save
from friendship.listeners import friendship_changed
from utils.memcached_helper import MemcachedHelper


# Create your models here.


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='followers_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('from_user', 'to_user'),)
        index_together = (
            ('from_user', 'created_at'),
            ('to_user', 'created_at')
        )

    def __str__(self):
        return f'{self.from_user_id} followed {self.from_user_id}'

    @property
    def cached_from_user(self):
        return MemcachedHelper.get_object_from_cache(model_class=User, object_id=self.from_user_id)

    @property
    def cached_to_user(self):
        return MemcachedHelper.get_object_from_cache(model_class=User, object_id=self.to_user_id)


# hook up with listeners to invalidate cache
pre_delete.connect(friendship_changed, sender=Friendship)
post_save.connect.connect(friendship_changed, sender=Friendship)
