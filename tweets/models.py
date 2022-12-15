from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from utils.time_helpers import utc_now

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet'
    )
    content = models.CharField(max_length=255)
    # CharField可以表示0~65535， 255是因为每个字符串自动加上\0保存，实际上是256 -1,
    created_at = models.DateTimeField(auto_now_add=True)
    # 每次创建时添加created_at这个字段，更新并不会改动,DateTimeField默认是有时区的，为服务器默认时区

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        # datetime.now不带时区信息，需要增加UTC的时区信息
        return (utc_now()-self.created_at).seconds // 3600

    # @property
    # def comments(self):
    #     # return Comment.objects.filter(tweet=self)
    #     return self.comment_set.all()

    def __str__(self):
        # 这是你执行 print(tweet instance)时会显示的内容
        return f'{self.created_at} {self.user}:{self.content}'

