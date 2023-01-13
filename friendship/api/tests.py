from rest_framework.test import APIClient
from testing.testcase import TestCase
from friendship.models import Friendship
from utils.pagination import FriendshipPagination

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
        self.assertEqual(len(response.data['results']), 2)
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(response.data['results'][0]['user']['username'], 'follower1 of user2')
        self.assertEqual(response.data['results'][1]['user']['username'], 'follower0 of user2')

    def test_following_api(self):
        url = FRIENDSHIP_GET_FOLLOWING_API.format(self.user2.id)
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        ts2 = response.data['results'][2]['created_at']

        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(response.data['results'][0]['user']['username'], 'following2 of user2')
        self.assertEqual(response.data['results'][1]['user']['username'], 'following1 of user2')
        self.assertEqual(response.data['results'][2]['user']['username'], 'following0 of user2')

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

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_results'], page_size*2)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size+1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 1, 'size': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

    def test_followers_pagination(self):
        page_size = FriendshipPagination.page_size
        max_page_size = FriendshipPagination.max_page_size

        for i in range(page_size*2):
            follower = self.create_user(username='user1_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user1)
            if i % 2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=follower)

        url = FRIENDSHIP_GET_FOLLOWERS_API.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        response = self.user2_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        for result in response.data['results']:
            if result['user']['id'] % 2 == 0:
                self.assertEqual(result['has_followed'], True)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            following = self.create_user('user1_following{}'.format(i))
            Friendship.objects.create(from_user=self.user1, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(from_user=self.user2, to_user=following)

        url = FRIENDSHIP_GET_FOLLOWING_API.format(self.user1.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous hasn't followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # dongxie has followed users with even id
        response = self.user2_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # linghu has followed all his following users
        response = self.user1_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)










