from celery import shared_task
from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR

@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
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
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create doesn't emit post_save signal, so, need to push each newsfeed to cache manually
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)