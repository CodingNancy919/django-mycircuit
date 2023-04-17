from celery import shared_task
from utils.time_constants import ONE_HOUR
from friendship.services import FriendshipService
from tweets.models import Tweet
from newsfeeds.models import NewsFeed
from newsfeeds.constants import FANOUT_BATCH_SIZE


@shared_task(time_limit=ONE_HOUR, routing_key='default')
def fanout_newsfeed_main_task(tweet_id):
    tweet = Tweet.objects.filter(id=tweet_id)
    # 将推给自己的 Newsfeed 率先创建，确保自己能最快看到
    NewsFeed.objects.create(user_id=tweet.user_id, tweet_id=tweet_id)
    # 获得所有的 follower ids，按照 batch size 拆分开
    followers_id = FriendshipService.get_all_followers_id(tweet.user)
    index = 0
    while index < len(followers_id):
        batch_ids = followers_id[index:index+FANOUT_BATCH_SIZE]
        fanout_newsfeed_batch_task.delay(tweet_id, batch_ids)
        index += FANOUT_BATCH_SIZE


@shared_task(time_limit=ONE_HOUR, routing_key='newsfeed')
def fanout_newsfeed_batch_task(tweet_id, followers_id):
    # import 写在里面避免循环依赖
    from newsfeeds.service import NewsFeedService

    # 错误的方法：将数据库操作放在 for 循环里面，效率会非常低 ->
    # for follower_id in followers_id:
    #     NewsFeed.objects.create(user_id=follower_id, tweet_id=tweet_id)
    # 正确的方法：使用 bulk_create，会把 insert 语句合成一条 ->
    newsfeeds = [NewsFeed(user_id=follower_id, tweet_id=tweet_id) for follower_id in followers_id]
    NewsFeed.objects.bulk_create(newsfeeds)
    # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
