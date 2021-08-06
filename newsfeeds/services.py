from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_task
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper

class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet):
        # this is to create a fanout task in message queue configured by celery
        # parameter is tweet. any worker monitoring the message query is able to get the task
        # the worker process will execute fanout_newsfeeds_task() to complete the async task
        # if the task need 10s, it will spend on worker process,
        # not spend on sending tweet process. so delay will be execute and finish immidiately.
        # note: delay parameter must be a value that can be celery to serialize
        # because worker process is independent process, even another machine.
        # so, it can't know what is value in memory of the web process.
        # thus, we send tweet.id as parameter instead of tweet. because celery doesn't
        # know how to serialize Tweet.
        fanout_newsfeeds_task.delay(tweet.id)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
