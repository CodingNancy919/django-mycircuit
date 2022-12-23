from testing.testcase import TestCase


class LikeModelTest(TestCase):

    def setUp(self):
        self.user = self.create_user(username='user1')
        self.tweet = self.create_tweet(self.user)
        self.comment = self.create_comment(self.user, self.tweet)
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_tweet(self):
        self.create_like(self.user, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.create_user(username='user2'), self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)

    def test_like_comment(self):
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.create_user(username='user2'), self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)

