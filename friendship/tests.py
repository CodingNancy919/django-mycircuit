from django.test import TestCase
import time

from django_hbase.models import EmptyColumnError, BadRowKeyError
from friendship.hbase_models import HBaseFollowers, HBaseFollowing


# Create your tests here.
class HBaseTests(TestCase):
    @property
    def ts_now(self):
        return int(time.time() * 1000000)

    def test_create_save_and_get(self):
        timestamp = self.ts_now
        following = HBaseFollowing(from_user_id=123, to_user_id=456, created_at=timestamp)
        following.save()

        instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
        self.assertEqual(instance.from_user_id, following.from_user_id)
        self.assertEqual(instance.to_user_id, following.to_user_id)
        self.assertEqual(instance.create_at, following.created_at)

        following.to_user_id = 4567
        following.save()

        instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
        self.assertEqual(instance.to_user_id, 4567)

        # object does not exist, return None
        instance = HBaseFollowing.get(from_user_id=123, created_at=self.ts_now)
        self.assertEqual(instance, None)

        # missing column data, can not store in hbase
        try:
            HBaseFollowing.create(from_user_id=123, created_at=timestamp)
            exception_raised = False
        except EmptyColumnError:
            exception_raised = True
        self.assertEqual(exception_raised, True)

        # invalid row_key
        try:
            HBaseFollowing.create(from_user_id=123, to_user_id=456)
            exception_raised = False
        except BadRowKeyError as e:
            exception_raised = True
            self.assertEqual(str(e), "created_at is missing in row key")
        self.assertEqual(exception_raised, True)

        timestamp = self.ts_now
        HBaseFollowing.create(from_user_id=123, to_user_id=456, created_at=timestamp)

        instance = HBaseFollowing.get(from_user_id=123, created_at=timestamp)
        self.assertEqual(instance.from_user_id, 123)
        self.assertEqual(instance.to_user_id, 456)
        self.assertEqual(instance.create_at, timestamp)

        # can not get if row key missing
        try:
            HBaseFollowing.create(to_user_id=456)
            exception_raised = False
        except BadRowKeyError as e:
            exception_raised = True
            self.assertEqual(str(e), "created_at is missing in row key")
        self.assertEqual(exception_raised, True)

    def test_filter(self):
        HBaseFollowing.create(from_user_id=1, to_user_id=2, created_at=self.ts_now)
        HBaseFollowing.create(from_user_id=1, to_user_id=3, created_at=self.ts_now)
        HBaseFollowing.create(from_user_id=1, to_user_id=4, created_at=self.ts_now)

        followings = HBaseFollowing.filter(prefix=(1, None, None))
        self.assertEqual(len(followings), 3)
        self.assertEqual(followings[0].from_user_id, 1)
        self.assertEqual(followings[0].to_user_id, 2)
        self.assertEqual(followings[1].from_user_id, 1)
        self.assertEqual(followings[1].to_user_id, 3)
        self.assertEqual(followings[2].from_user_id, 1)
        self.assertEqual(followings[2].to_user_id, 4)

        # test limit
        followings = HBaseFollowing.filter(prefix=(1, None, None), limit=1)
        self.assertEqual(len(followings), 1)
        self.assertEqual(followings[0].to_user_id, 2)

        followings = HBaseFollowing.filter(prefix=(1, None, None), limit=2)
        self.assertEqual(len(followings), 2)
        self.assertEqual(followings[0].to_user_id, 2)
        self.assertEqual(followings[1].to_user_id, 3)

        followings = HBaseFollowing.filter(prefix=(1, None, None), limit=4)
        self.assertEqual(len(followings), 3)
        self.assertEqual(followings[0].to_user_id, 2)
        self.assertEqual(followings[1].to_user_id, 3)
        self.assertEqual(followings[2].to_user_id, 4)

        followings = HBaseFollowing.filter(start=(1, followings[1].created_at, None), limit=2)
        self.assertEqual(len(followings), 2)
        self.assertEqual(followings[0].to_user_id, 3)
        self.assertEqual(followings[1].to_user_id, 4)

        # test reverse
        followings = HBaseFollowing.filter(prefix=(1, None, None), limit=2, reverse=True)
        self.assertEqual(len(followings), 2)
        self.assertEqual(followings[0].to_user_id, 4)
        self.assertEqual(followings[1].to_user_id, 3)

        followings = HBaseFollowing.filter(start=(1, followings[1].created_at, None), limit=2, reverse=True)
        self.assertEqual(len(followings), 2)
        self.assertEqual(followings[0].to_user_id, 3)
        self.assertEqual(followings[1].to_user_id, 2)


