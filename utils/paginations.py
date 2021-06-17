from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FriendshipPagination(PageNumberPagination):
    # https://.../api/friendships/1/followers/?page=3&size=10
    # Default page_size when page is not in url query parameters.
    page_size = 20
    # Default page_size_query_param is None. It means customer can't specify the page size
    # Adding this config, customer can specify the size for different scenarios such as web or phone.
    page_size_query_param = 'size'
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
                'total_results': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'page_number': self.page.number,
                'has_next_page': self.page.has_next(),
                'results': data,
        })
