def friendship_changed(sender, instance, **kwags):
    from friendship.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)