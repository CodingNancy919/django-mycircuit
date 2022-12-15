from rest_framework.test import APIClient
from testing.testcase import TestCase
from comments.models import Comment


# 注意要加 '/' 结尾，要不然会产生 301 redirect
COMMENT_API = '/api/comments/'

class CommentApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(user=self.user1)

    def test_comment_api(self):
        response = self.anonymous_client.post(COMMENT_API)
        self.assertEqual(response.status_code, 403)

        response = self.user2_client.get(COMMENT_API)
        self.assertEqual(response.status_code, 405)

        response = self.user2_client.post(COMMENT_API)
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id, 'content': '1'*141})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id, 'content': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user2.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['comment'], '1')

