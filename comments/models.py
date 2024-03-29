from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from utils.memcached_helper import MemcachedHelper
from comments.listeners import incr_comments_count, decr_comments_count
from django.db.models.signals import pre_delete, post_save


class Comment(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    tweet = models.ForeignKey(Tweet, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        index_together = (('tweet', 'created_at'),)

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(self.__class__),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        return "{} {} says {} about tweet{}".format(
            self.created_at,
            self.user,
            self.comment,
            self.tweet_id,
        )

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_from_cache(model_class=User, object_id=self.user_id)

    @property
    def cached_tweet(self):
        return MemcachedHelper.get_object_from_cache(model_class=Tweet, object_id=self.tweet_id)


post_save.connect(incr_comments_count, sender=Comment)
pre_delete.connect(decr_comments_count, sender=Comment)


