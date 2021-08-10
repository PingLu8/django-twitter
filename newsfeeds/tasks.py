from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR
from newsfeeds.constants import FANOUT_BATCH_SIZE

@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    # import written inside of method to avoid reference loop.
    from newsfeeds.services import NewsFeedService

    # wrong way:
    # can not put db operation in for loop. efficiency is super low and slow
    # for follower in FriendshipService.get_followers(tweet.user):
    #   NewsFeed.objects.create(
    #       user=follower,
    #       tweet=tweet,
    #   )
    # correct way: use bulk_create, then insert once
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create doesn't emit post_save signal, so, need to push each newsfeed to cache manually
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)
    return '{} newsfeeds created'.format(len(newsfeeds))

@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    # create newsfeed for tweet owner himself, so, he can see the tweet quickly
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # get the follower ids, split newsfeeds count based on batch size
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    index = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index: index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_ids)
        index += FANOUT_BATCH_SIZE

    return '{} newsfeeds going to fanout, {} batches created.'.format(
            len(follower_ids),
            (len(follower_ids) - 1) // FANOUT_BATCH_SIZE + 1,
    )