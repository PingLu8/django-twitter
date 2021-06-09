from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    #oneToOne relationship will create a unique index, to ensure no multiple UserProfiles point to a user.
    #user foreign key to ensure only one user point to one UserProfile.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    avatar = models.FileField(null=True)

    nickname = models.CharField(null=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.nickname)

def get_profile(user):
        if hasattr(user, '_cached_user_profile'):
            return getattr(user, '_cached_user_profile')
        profile, _ = UserProfile.objects.get_or_create(user=user)
        setattr(user, '_cached_user_profile', profile)
        return profile
# add a property to User model
User.profile = property(get_profile)