from testing.testcase import TestCase


LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


class LikeModelTest(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')

    def test_like_tweet(self):
        tweet = self.create_tweet(self.user1)
        data = {'content_type': 'tweet', 'object_id': tweet.id}

        response = self.anonymous_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 403)

        response = self.user1_client.get(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 405)

        response = self.user1_client.post(LIKE_BASE_URL)
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(LIKE_BASE_URL, {'content_type': 'coment'})
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(LIKE_BASE_URL, {'content_type': 'comment', 'object_id': -1})
        self.assertEqual(response.status_code, 400)
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(tweet.like_set.count(), 1)

        response = self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)

    def test_like_comment(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        data = {'content_type': 'comment', 'object_id': comment.id}

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'coment',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('object_id' in response.data['errors'], True)

        # post success
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)

        # duplicate likes
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(comment.like_set.count(), 1)
        self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)

    def test_cancel(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        like_comment_data = {'content_type': 'comment', 'object_id': comment.id}
        like_tweet_data = {'content_type': 'tweet', 'object_id': tweet.id}
        self.user1_client.post(LIKE_BASE_URL, like_comment_data)
        self.user2_client.post(LIKE_BASE_URL, like_tweet_data)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # login required
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)

        # get is not allowed
        response = self.user1_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)

        # wrong content_type
        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong',
            'object_id': 1,
        })
        self.assertEqual(response.status_code, 400)

        # wrong object_id
        response = self.user1_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, 400)

        # dongxie has not liked before
        response = self.user2_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)

        # successfully canceled
        response = self.user1_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # linghu has not liked before
        response = self.user1_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 0)

        # dongxie's like has been canceled
        response = self.user2_client.post(LIKE_CANCEL_URL, like_tweet_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tweet.like_set.count(), 0)
        self.assertEqual(comment.like_set.count(), 0)

    def test_likes_in_comment(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user1, tweet)
        response = self.anonymous_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        response = self.user2_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.user2, comment)
        response = self.user2_client.get(COMMENT_LIST_API, {"tweet_id": tweet.id})
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)

        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)




    def test_likes_in_tweet(self):
        # test tweet detail api
        tweet = self.create_tweet(self.user1)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user1_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.user2, tweet)
        response = self.user2_client.get(url)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        # test tweets list api
        response = self.user1_client.get(TWEET_LIST_API, {"user_id": self.user1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['has_liked'], False)
        self.assertEqual(response.data['results'][0]['likes_count'], 1)
        # test newsfeeds list api
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['tweet']['has_liked'], True)
        self.assertEqual(response.data['results'][0]['tweet']['likes_count'], 1)
        # test likes details
        self.create_like(self.user1, tweet)
        response = self.user1_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        print(response.data['likes'])
        # self.assertEqual(response.data['likes'][0]['user']['id'], self.user1.id)
        # self.assertEqual(response.data['likes'][1]['user']['id'], self.user2.id)

    def test_likes_count(self):
        tweet = self.create_tweet(self.user1)
        data = {'content_type': 'tweet', 'object_id': tweet.id}
        self.user1_client.post(LIKE_BASE_URL, data)

        tweet_url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user1_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 1)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 1)

        # user2 canceled likes
        self.user1_client.post(LIKE_BASE_URL + 'cancel/', data)
        tweet.refresh_from_db()
        self.assertEqual(tweet.likes_count, 0)
        response = self.user2_client.get(tweet_url)
        self.assertEqual(response.data['likes_count'], 0)

