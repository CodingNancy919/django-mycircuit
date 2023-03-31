def invalidate_following_cache(cls, from_user_id):
    from friendship.service import FriendshipService
    FriendshipService.invalidate_following_cache(from_user_id=from_user_id)