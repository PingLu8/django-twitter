from django.db import models
from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializer, UserSerializerForTweet
from utils.time_helpers import utc_now
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache


class Tweet(models.Model):
    user = UserSerializerForTweet
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
        )
        ordering = ('user', '-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'

    @property
    def hours_to_now(self):
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)

# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(invalidate_object_cache, sender=Tweet)