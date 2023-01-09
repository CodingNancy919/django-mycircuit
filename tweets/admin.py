from django.contrib import admin
from tweets.models import Tweet, TweetPhoto


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'content',
        'created_at',
    )


@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'tweet',
        'file',
        'order',
        'status',
        'has_deleted',
        'created_at',
    )
    list_filter = ('status', 'has_deleted')

