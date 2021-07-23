def user_changed(sender, instance, **kwargs):
    # import in the method to avoid the reference loop
    from accounts.services import UserService
    UserService.invalidate_user(instance.id)

def profile_changed(sender, instance, **kwargs):
    from accounts.services import UserService
    UserService.invalidate_profile(instance.user_id)