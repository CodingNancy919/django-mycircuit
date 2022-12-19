from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Like(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    # comment id or tweet id
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 这里使用 unique together 也就会建一个 <user, content_type, object_id>
        # 的索引。这个索引同时还可以具备查询某个 user like 了哪些不同的 objects 的功能
        # 因此如果 unique together 改成 <content_type, object_id, user>
        # 就没有这样的效果了
        unique_together = (
            ('content_type', 'object_id', 'user'),
        )

        index_together = (
            # 这个 index 的作用是可以按时间排序某个content_object(tweet/comment) 的所有 likes
            ('content_type', 'object_id', 'created_at'),
            # 这个 index 的作用是可以按时间排序某个user对tweet or comment 的所有 likes
            ('user', 'content_type', 'created_at'),
            # 这个 index 的作用是可以按时间排序某个user对tweet and comment 的所有 likes...
            ('user', 'created_at'),
        )

    def __str__(self):
        return "{} - {} likes {}.{}".format(
            self.created_at,
            self.user,
            self.content_type,
            self.object_id,

        )

