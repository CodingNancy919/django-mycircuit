from django.contrib import admin
from friendship.models import Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'id',
        'created_at',
        'from_user',
        'to_user',
    )
