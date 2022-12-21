from testing.testcase import TestCase
from notifications.models import Notification

LIKE_BASE_URL = '/api/likes/'
COMMENT_API = '/api/comments/'


class NotificationServiceAPITest(TestCase):
    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client(username='user1')
        self.user2, self.user2_client = self.create_user_and_client(username='user2')

    def test_create_like_trigger_notifications(self):
        tweet = self.create_tweet(self.user1)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 0)

        response = self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)

    def test_create_comment_trigger_notifications(self):
        tweet = self.create_tweet(self.user1)
        response = self.user1_client.post(COMMENT_API, {'tweet_id': tweet.id, 'comment': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 0)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': tweet.id, 'comment': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)
