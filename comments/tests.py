from testing.testcase import TestCase
from comments.models import Comment


class CommentModelTest(TestCase):
    def test_comment(self):
        user = self.create_user(username='Nancy')
        tweet = self.create_tweet(user)
        comment = self.create_comment(user=user, tweet=tweet, content='my comment')
        self.assertNotEqual(comment.__str__(), None)
