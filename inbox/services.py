from notifications.signals import notify
from tweets.models import Tweet
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType


class NotificationService(object):

    @classmethod
    def send_like_notifications(cls, like):
        target = like.content_object
        if like.user == target.user:
            return
        if like.content_type == ContentType.objects.get_for_model(Tweet):
            notify.send(
                like.user,
                recipient=target.user,
                verb='like your tweet',
                target=target
            )
        if like.content_type == ContentType.objects.get_for_model(Comment):
            notify.send(
                like.user,
                recipient=target.user,
                verb='like your comment',
                target=target)

    @classmethod
    def send_comment_notifications(cls, comment):
        tweet = comment.tweet
        if comment.user == tweet.user:
            return
        notify.send(
            comment.user,
            recipient=tweet.user,
            verb='comment your tweet',
            target=tweet
        )