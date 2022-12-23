from rest_framework.test import APIClient
from testing.testcase import TestCase
from friendship.models import Friendship


# 注意要加 '/' 结尾，要不然会产生 301 redirect
FRIENDSHIP_GET_FOLLOWERS_API = '/api/friendship/{}/followers/'
FRIENDSHIP_GET_FOLLOWING_API = '/api/friendship/{}/following/'
FRIENDSHIP_FOLLOW_API = '/api/friendship/{}/follow/'
FRIENDSHIP_UNFOLLOW_API = '/api/friendship/{}/unfollow/'


class FriendshipApiTests(TestCase):

    def setUp(self):

        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)
        for i in range(2):
            newuser = self.create_user("follower{} of user2".format(i))
            Friendship.objects.create(from_user=newuser, to_user=self.user2)

        for i in range(3):
            newuser = self.create_user("following{} of user2".format(i))
            Friendship.objects.create(from_user=self.user2, to_user=newuser)

    def test_followers_api(self):
        url = FRIENDSHIP_GET_FOLLOWERS_API.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['followers'][0]['user']['username'], 'follower1 of user2')
        self.assertEqual(response.data['followers'][1]['user']['username'], 'follower0 of user2')

    def test_following_api(self):
        url = FRIENDSHIP_GET_FOLLOWING_API.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']

        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(response.data['followings'][0]['user']['username'], 'following2 of user2')
        self.assertEqual(response.data['followings'][1]['user']['username'], 'following1 of user2')
        self.assertEqual(response.data['followings'][2]['user']['username'], 'following0 of user2')

    def test_follow_api(self):
        url = FRIENDSHIP_FOLLOW_API.format(self.user2.id)
        # must be POST method
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)
        # must be authenticated
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # must not follow yourself
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)
        # success
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)
        # 静默处理
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        count = Friendship.objects.count()
        response = self.user2_client.post(FRIENDSHIP_FOLLOW_API.format(self.user1.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count+1)

    def test_unfollow_api(self):
        url = FRIENDSHIP_UNFOLLOW_API.format(self.user2.id)
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 405)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 400)

        Friendship.objects.create(from_user=self.user1, to_user=self.user2)
        count = Friendship.objects.count()
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)



