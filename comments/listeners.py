from utils.listeners import object_changed


def incr_comments_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count')+1)
    object_changed(sender=Tweet, instance=instance.tweet)

    # tweet = Tweet.objects.filter(id=instance.object_id)
    # tweet.comments_count = F('comments_count')+1


def decr_comments_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    Tweet.objects.filter(id=instance.tweet_id).update(comments_count=F('comments_count') - 1)
    object_changed(sender=Tweet, instance=instance.tweet)

    # tweet = Tweet.objects.filter(id=instance.object_id)
    # tweet.comments_count = F('comments_count')-1


