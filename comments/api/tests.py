from rest_framework.test import APIClient
from testing.testcase import TestCase
from comments.models import Comment
from utils.time_helpers import utc_now
from django.utils import timezone
# 注意要加 '/' 结尾，要不然会产生 301 redirect
COMMENT_API = '/api/comments/'
TWEET_DETAIL_API = '/api/tweets/{}/'
TWEET_LIST_API = '/api/tweets/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class CommentApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@jiuzhang.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@jiuzhang.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(user=self.user1)

    def test_create_comment(self):
        response = self.anonymous_client.post(COMMENT_API)
        self.assertEqual(response.status_code, 403)

        # response = self.user2_client.get(COMMENT_API, {'tweet_id': self.tweet.id})
        # self.assertEqual(response.status_code, 405)

        response = self.user2_client.post(COMMENT_API)
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id, 'comment': '1'*141})
        self.assertEqual(response.status_code, 400)

        response = self.user2_client.post(COMMENT_API, {'tweet_id': self.tweet.id, 'comment': '1'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user2.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['comment'], '1')

    def test_delete_comment(self):
        self.comment = self.create_comment(self.user1, self.tweet)
        url = '{}{}/'.format(COMMENT_API, self.comment.id)

        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code,  403)

        response = self.user2_client.delete(url)
        self.assertEqual(response.status_code, 403)

        count = Comment.objects.count()
        response = self.user1_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count-1)

    def test_update_comment(self):
        self.comment = self.create_comment(self.user1, self.tweet)
        url = '{}{}/'.format(COMMENT_API, self.comment.id)

        response = self.anonymous_client.put(url)
        self.assertEqual(response.status_code,  403)

        response = self.user2_client.put(url)
        self.assertEqual(response.status_code, 403)

        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.comment, 'new')
        before_created_at = self.comment.created_at
        before_updated_at = self.comment.updated_at
        count = Comment.objects.count()

        now = timezone.now()
        response = self.user1_client.put(url, {
            # 'user_id': self.user1.id,
            # 'tweet_id': self.tweet.id,
            'comment': 'new',
            'created_at': now
        })
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.user_id, self.user1.id)
        self.assertEqual(self.comment.tweet, self.tweet)
        self.assertEqual(self.comment.comment, 'new')
        self.assertEqual(self.comment.created_at, before_created_at)
        self.assertNotEqual(self.comment.created_at, now)
        self.assertNotEqual(self.comment.updated_at, before_updated_at)

    def test_list(self):
        # 必须带 tweet_id
        response = self.anonymous_client.get(COMMENT_API)
        self.assertEqual(response.status_code, 400)

        # 带了 tweet_id 可以访问
        # 一开始没有评论
        response = self.anonymous_client.get(COMMENT_API, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # 评论按照时间顺序排序
        self.create_comment(self.user1, self.tweet, '1')
        self.create_comment(self.user2, self.tweet, '2')
        self.create_comment(self.user2, self.create_tweet(self.user2), '3')
        response = self.anonymous_client.get(COMMENT_API, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['comment'], '1')
        self.assertEqual(response.data['comments'][1]['comment'], '2')

        # 同时提供 user_id 和 tweet_id 只有 tweet_id 会在 filter 中生效
        response = self.anonymous_client.get(COMMENT_API, {
            'tweet_id': self.tweet.id,
            'user_id': self.user1.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.user1)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.user1, tweet)
        response = self.user2_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.user2, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['comments_count'], 2)


