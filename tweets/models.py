from django.db import models
from django.contrib.auth.models import User
from accounts.api.serializers import UserSerializer, UserSerializerForTweet
from utils.time_helpers import utc_now
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from utils.memcached_helper import MemcachedHelper
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache
from tweets.listeners import push_tweet_to_cache
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES


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
        # datetime.now doesn't have timezone info,
        # so, need to use utc to get timezone info
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

class TweetPhoto(models.Model):

    # which tweet the photo is associating with.
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # who update the photo. although the info about who can get from tweet as well.
    # redundant store user_id info in photo, we can filter photos based on user_id.
    # thus, we someone keep uploading illegal photos, we can focus audit the person's photos.
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # photo files
    file = models.FileField()
    order = models.IntegerField(default=0)

    # photo status, waiting for audit case:
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # soft delete, mark the photo is deleted, after a certain time, the marked photos will be deleted from db.
    # This is due to delete photo takes time and affect the performance. so we can use async task to perform the real
    # delete action at backend.
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


# hook up with listeners to invalidate cache
pre_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache, sender=Tweet)