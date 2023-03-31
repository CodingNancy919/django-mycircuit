
def user_changed(sender, instance, **kwags):
    from accounts.services import UserService
    UserService.invalidate_user_cache(instance.id)


def userprofile_changed(sender, instance, **kwags):
    from accounts.services import UserProfileService
    UserProfileService.invalidate_userprofile_cache(instance.user_id)
