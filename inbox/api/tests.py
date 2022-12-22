from testing.testcase import TestCase
from notifications.models import Notification

LIKE_BASE_URL = '/api/likes/'
COMMENT_URL = '/api/comments/'
NOTIFICATION_URL = '/api/notifications/'
NOTIFICATION_UNREAD_COUNT_URL = '/api/notifications/unread-count/'
NOTIFICATION_MARK_ALL_READ_URL = '/api/notifications/mark-all-as-read/'


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
        response = self.user1_client.post(COMMENT_URL, {'tweet_id': tweet.id, 'comment': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 0)

        response = self.user2_client.post(COMMENT_URL, {'tweet_id': tweet.id, 'comment': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)


class NotificationApiTests(TestCase):

    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client(username='user1')
        self.user2, self.user2_client = self.create_user_and_client(username='user2')
        self.tweet = self.create_tweet(self.user1)

    def test_unread_count(self):
        data = {'content_type': 'tweet', 'object_id': self.tweet.id}
        self.user2_client.post(LIKE_BASE_URL, data)

        response = self.anonymous_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 403)
        response = self.user1_client.post(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)
        response = self.user2_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

        response = self.user1_client.post(COMMENT_URL, {'comment': 'test', 'tweet_id': self.tweet.id})
        data = {'content_type': 'comment', 'object_id': response.data['id']}
        self.user2_client.post(LIKE_BASE_URL, data)

        response = self.user2_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)
        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)

    def test_mark_all_as_read(self):
        data = {'content_type': 'tweet', 'object_id': self.tweet.id}
        self.user2_client.post(LIKE_BASE_URL, data)
        response = self.user1_client.post(COMMENT_URL, {'comment': 'test', 'tweet_id': self.tweet.id})
        data = {'content_type': 'comment', 'object_id': response.data['id']}
        self.user2_client.post(LIKE_BASE_URL, data)

        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)

        response = self.anonymous_client.get(NOTIFICATION_MARK_ALL_READ_URL)
        self.assertEqual(response.status_code, 403)
        response = self.user1_client.get(NOTIFICATION_MARK_ALL_READ_URL)
        self.assertEqual(response.status_code, 405)
        response = self.user1_client.post(NOTIFICATION_MARK_ALL_READ_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['update_count'], 2)
        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

        response = self.user2_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 0)

    def test_update_read(self):
        data = {'content_type': 'tweet', 'object_id': self.tweet.id}
        self.user2_client.post(LIKE_BASE_URL, data)
        response = self.user1_client.post(COMMENT_URL, {'comment': 'test', 'tweet_id': self.tweet.id})
        data = {'content_type': 'comment', 'object_id': response.data['id']}
        self.user2_client.post(LIKE_BASE_URL, data)
        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)

        instance = self.user1.notifications.first()
        url = '/api/notifications/{}/'.format(instance.id)
        response = self.anonymous_client.put(url)
        self.assertEqual(response.status_code, 403)
        response = self.user2_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 404)
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.put(url)
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.put(url, {'unread': False})
        self.assertEqual(response.status_code, 200)
        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 1)

        response = self.user1_client.put(url, {'unread': True})
        self.assertEqual(response.status_code, 200)
        response = self.user1_client.get(NOTIFICATION_UNREAD_COUNT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['unread_count'], 2)



    def test_list(self):
        self.user2_client.post(LIKE_BASE_URL, {
            'content_type': 'tweet',
            'object_id': self.tweet.id,
        })
        comment = self.create_comment(self.user1, self.tweet)
        self.user2_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': comment.id,
        })

        # 匿名用户无法访问 api
        response = self.anonymous_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 403)
        # dongxie 看不到任何 notifications
        response = self.user2_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        # linghu 看到两个 notifications
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        # 标记之后看到一个未读
        notification = self.user1.notifications.first()
        notification.unread = False
        notification.save()
        response = self.user1_client.get(NOTIFICATION_URL)
        self.assertEqual(len(response.data), 2)
        # response = self.linghu_client.get(NOTIFICATION_URL, {'unread': True})
        # self.assertEqual(len(response.data), 1)
        # response = self.linghu_client.get(NOTIFICATION_URL, {'unread': False})
        # self.assertEqual(len(response.data), 1)

