
def incr_likes_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class is Tweet:
        # 不可以使用 tweet.likes_count += 1; tweet.save() 的方式
        # 因此这个操作不是原子操作，必须使用 update 语句才是原子操作
        Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count')+1)

        # tweet = Tweet.objects.filter(id=instance.object_id)
        # tweet.likes_count = F('likes_count')+1


def decr_likes_count(sender, instance, created, **kwags):
    from tweets.models import Tweet
    from django.db.models import F

    if not created:
        return

    model_class = instance.content_type.model_class()
    if model_class is Tweet:
        # 不可以使用 tweet.likes_count += 1; tweet.save() 的方式
        # 因此这个操作不是原子操作，必须使用 update 语句才是原子操作
        Tweet.objects.filter(id=instance.object_id).update(likes_count=F('likes_count') - 1)

        # tweet = Tweet.objects.filter(id=instance.object_id)
        # tweet.likes_count = F('likes_count')-1


