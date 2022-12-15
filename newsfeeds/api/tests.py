from rest_framework.test import APIClient
from testing.testcase import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendship/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.anonymous_client = APIClient()

        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list_api(self):
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # 正常 request
        response = self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        self.assertEqual(response.status_code, 201)
        response = self.user2_client.post(POST_TWEETS_URL, {'content': 'This is a test tweet'})
        posted_twitter_id = response.data['id']
        response = self.user2_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_twitter_id)

