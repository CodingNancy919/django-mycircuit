from testing.testcase import TestCase
from notifications.models import Notification

LIKE_BASE_URL = '/api/likes/'
COMMENT_API = '/api/comments/'

COMMENT_URL = '/api/comments/'
LIKE_URL = '/api/likes/'
NOTIFICATION_URL = '/api/notifications/'


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


class NotificationApiTests(TestCase):

    def setUp(self):
        self.linghu, self.linghu_client = self.create_user_and_client('linghu')
        self.dongxie, self.dongxie_client = self.create_user_and_client('dongxie')
        self.linghu_tweet = self.create_tweet(self.linghu)

    def test_unread_count(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })

        url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })
        response = self.linghu_client.get(url)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        unread_url = '/api/notifications/unread-count/'
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 2)

        mark_url = '/api/notifications/mark-all-as-read/'
        response = self.linghu_client.get(mark_url)
        self.assertEqual(response.status_code, 405)
        response = self.linghu_client.post(mark_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['update_count'], 2)
        response = self.linghu_client.get(unread_url)
        self.assertEqual(response.data['unread_count'], 0)

    def test_list(self):
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'tweet',
            'object_id': self.linghu_tweet.id,
        })
        comment = self.create_comment(self.linghu, self.linghu_tweet)
        self.dongxie_client.post(LIKE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户无法访问 api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # dongxie 看不到任何 notifications
        response = self.dongxie_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        # linghu 看到两个 notifications
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # 标记之后看到一个未读
        notification = self.linghu.notifications.first()
        notification.unread = False
        notification.save()
        response = self.linghu_client.get(NOTIFICATION_URL)
        self.assertEqual(len(response.data), 2)
        # response = self.linghu_client.get(NOTIFICATION_URL, {'unread': True})
        # self.assertEqual(len(response.data), 1)
        # response = self.linghu_client.get(NOTIFICATION_URL, {'unread': False})
        # self.assertEqual(len(response.data), 1)
