from friendships.models import Friendship

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):

        # wrong implementation 1. For loop can't contain query. too slow
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # wrong implementation 2. Join is not allowed in big data table.
        # when using select_related('from_user'), it already left join and contains from_user
        # in friendships. so, the For loop doesn't has sql query to get from_user.
        # friendships = Friendship.objects.filter(to_user=user).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # correct implementation 1.
        # friendships = Friendship.objects.filter(to_user=user)
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # correct implementation 2.
        friendships = Friendship.objects.filter(to_user=user).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]