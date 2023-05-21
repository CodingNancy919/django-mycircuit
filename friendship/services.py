import time

from friendship.models import Friendship
from django.contrib.auth.models import User
from twitter.cache import FOLLOWING_PATTERN
from django.utils.cache import caches
from django.conf import settings
from gatekeeper.models import GateKeeper
from friendship.hbase_models import HBaseFollowing, HBaseFollowers

cache = caches['default'] if settings.TESTING else caches['testing']


class FriendshipService(object):
    @classmethod
    def get_all_followers(cls, user):
        # 错误的写法一
        # 这种写法会导致 N + 1 Queries 的问题
        # 即，filter 出所有 friendships 耗费了一次 Query
        # 而 for 循环每个 friendship 取 from_user 又耗费了 N 次 Queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误的写法二
        # 这种写法是使用了 JOIN 操作，让 friendship table 和 user table 在 from_user
        # 这个属性上 join 了起来。join 操作在大规模用户的 web 场景下是禁用的，因为非常慢。
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 正确的写法一，自己手动 filter id，使用 IN Query 查询
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # 正确的写法二，使用 prefetch_related，会自动执行成两条语句，用 In Query 查询
        # 实际执行的 SQL 查询和上面是一样的，一共两条 SQL Queries
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)
        # return followers
        friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def get_all_followers_id(cls, user):
        friendships = Friendship.objects.filter(to_user=user)
        return [friendship.from_user_id for friendship in friendships]

    @classmethod
    def has_followed(cls, from_user, to_user):
        return Friendship.objects.filter(
            from_user=from_user,
            to_user=to_user
        ).exists()

    @classmethod
    # 每次web server访问memcache的时候，缓存不会被释放 除非超时或主动释放, 或者由于LFU淘汰机由于key的访问频率不高被删掉
    def get_following_user_id_set(cls, from_user_id):
        # 数据库get得到的结果如果为空一般会有异常try catch处理 cache则返回none
        #
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        following_user_id_set = cache.get(key)
        if following_user_id_set is not None:
            return following_user_id_set
        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        # memcached本身只支持string类型，set类型是django对memcached的支持
        following_user_id_set = set([friendship.to_user_id for friendship in friendships])
        cache.set(key, following_user_id_set)
        return following_user_id_set

    # +5 read {1,2,4} -> {1,2,4,5}
    # +6 read {1,2,4} -> {1,2,4,6}
    # 删除key带来的data consistency小于添加key race condition
    # 由于web server和cache server不在一台机器上，没法加锁，不共享内存 一般通过TTL来解决数据不一致性

    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWING_PATTERN.format(user_id=from_user_id)
        cache.delete(key)

    @classmethod
    def follow(cls, from_user_id, to_user_id):
        if from_user_id == to_user_id:
            return None
        # create data in mysql
        if not GateKeeper.is_switch_on('switch_friendship_to_hbase'):
            return Friendship.objects.create(from_user_id=from_user_id, to_user_id=to_user_id)

        # create data in hbase
        now = int(time.time() * 1000000)
        HBaseFollowing.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now
        )
        HBaseFollowers.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            created_at=now
        )








