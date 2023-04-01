
def push_tweet_to_cache(sender, instance, created, **kwags):
    if not created:
        return
    from tweets.services import TweetService
    TweetService.push_tweet_to_cache(instance)

