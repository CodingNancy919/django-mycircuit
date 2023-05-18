from tweets.models import TweetPhoto
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_helper import RedisHelper
from tweets.models import Tweet


class TweetService(object):
    @classmethod
    def create_photos_from_files(cls, tweet, files):
        tweet_photos = []
        for index, photo in enumerate(files):
            tweet_photo = TweetPhoto(
                tweet=tweet,
                file=photo,
                order=index,
                user=tweet.user,
            )
            tweet_photos.append(tweet_photo)
        TweetPhoto.objects.bulk_create(tweet_photos)

    @classmethod
    def get_cached_tweets(cls, user_id):
        key = USER_TWEETS_PATTERN.format(user_id=user_id)

        # django queryset use lazy loading 此时并不会产生数据库查询 在调用queryset具体的操作时才会访问
        queryset = Tweet.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
        return RedisHelper.get_objects(key, queryset)

    @classmethod
    def push_tweet_to_cache(cls, tweet):
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        # django lazy loading 此时并不会产生数据库查询 在调用queryset具体的操作时才会访问
        queryset = Tweet.objects.filter(
            user_id=tweet.user_id
        ).order_by('-created_at')
        return RedisHelper.push_object(key, tweet, queryset)


    # 此处有一个问题 如果用户更改推文 Redis内存中的内容并不会更新 是否有更好的设计？
    # 可以用redis存放tweet_id 列表 memcached存放具体的tweets 优点是一致性更高 缺点是增加了memcached的负载
    # cache.getmany() Tweet.objects.filter(id__in([1,2,3]))


