from django.contrib import admin
from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'user',
        'tweet',
        'comment',
        'created_at',
        'updated_at',
    )
