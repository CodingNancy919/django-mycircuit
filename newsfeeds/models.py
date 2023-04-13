from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import pre_delete, post_save
from newsfeeds.listeners import push_newsfeed_to_cache


class NewsFeed(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='user_newsfeed_set'
    )
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'tweet'),)
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user} can see {self.tweet}'

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_from_cache(model_class=User, object_id=self.user_id)

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_from_cache(model_class=Tweet, object_id=self.tweet_id)


post_save.connect(push_newsfeed_to_cache, sender=NewsFeed)
