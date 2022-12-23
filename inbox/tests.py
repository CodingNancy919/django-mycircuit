from testing.testcase import TestCase
from inbox.services import NotificationService
from notifications.models import Notification


class NotificationServiceTest(TestCase):
    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.user2 = self.create_user(username='user2')
        self.tweet = self.create_tweet(self.user1)

    def test_send_like_notifications(self):
        like = self.create_like(self.user1, self.tweet)
        NotificationService.send_like_notifications(like)
        self.assertEqual(Notification.objects.count(), 0)

        like = self.create_like(self.user2, self.tweet)
        NotificationService.send_like_notifications(like)
        self.assertEqual(Notification.objects.count(), 1)

    def test_send_comment_notifications(self):
        comment = self.create_comment(self.user1, self.tweet)
        NotificationService.send_comment_notifications(comment)
        self.assertEqual(Notification.objects.count(), 0)

        comment = self.create_comment(self.user2, self.tweet)
        NotificationService.send_comment_notifications(comment)
        self.assertEqual(Notification.objects.count(), 1)
