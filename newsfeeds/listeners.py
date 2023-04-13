
def push_newsfeed_to_cache(sender, instance, created, **kwags):
    if not created:
        return
    from newsfeeds.service import NewsFeedService
    NewsFeedService.push_newsfeed_to_cache(instance)

