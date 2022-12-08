from django.contrib import admin
from friendship.models import Friendship


@admin.register(Friendship)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'from_user',
        'to_user',
    )
