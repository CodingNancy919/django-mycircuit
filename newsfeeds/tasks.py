from celery import shared_task
from utils.time_constants import ONE_HOUR
from friendship.services import FriendshipService
from tweets.models import Tweet
from newsfeeds.models import NewsFeed


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeed_task(tweet_id):
    # import 写在里面避免循环依赖
    from newsfeeds.service import NewsFeedService

    # 错误的方法
    # 不可以将数据库操作放在 for 循环里面，效率会非常低
    # for follower in FriendshipService.get_followers(tweet.user):
    #     NewsFeed.objects.create(
    #         user=follower,
    #         tweet=tweet,
    #     )
    # 正确的方法：使用 bulk_create，会把 insert 语句合成一条
    tweet = Tweet.objects.filter(id=tweet_id)
    followers = FriendshipService.get_all_followers(tweet.user)
    newsfeeds = [NewsFeed(user=follower, tweet=tweet) for follower in followers]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)
    # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
