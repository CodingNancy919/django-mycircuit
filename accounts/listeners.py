
def userprofile_changed(sender, instance, **kwags):
    from accounts.services import UserProfileService
    UserProfileService.invalidate_userprofile_cache(instance.user_id)
