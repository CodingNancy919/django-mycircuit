from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='following_friendship_set',
    )

    to_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='followers_friendship_set',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('from_user', 'to_user'),)
        index_together = (
            ('from_user', 'created_at'),
            ('to_user', 'created_at')
        )

    def __str__(self):
        return f'{self.from_user_id} followed {self.from_user_id}'
