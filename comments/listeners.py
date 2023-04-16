from utils.listeners import object_changed
from utils.redis_helper import RedisHelper


def incr_comments_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    tweet = instance.tweet
    Tweet.objects.filter(id=tweet.id).update(comments_count=F('comments_count')+1)
    object_changed(sender=Tweet, instance=tweet)
    RedisHelper.incr_count(tweet, "comments_count")

    # tweet = Tweet.objects.filter(id=instance.object_id)
    # tweet.comments_count = F('comments_count')+1


def decr_comments_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return
    tweet = instance.tweet
    Tweet.objects.filter(id=tweet.id).update(comments_count=F('comments_count') - 1)
    object_changed(sender=Tweet, instance=tweet)
    RedisHelper.decr_count(tweet, "comments_count")

    # tweet = Tweet.objects.filter(id=instance.object_id)
    # tweet.comments_count = F('comments_count')-1


