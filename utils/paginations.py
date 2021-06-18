from rest_framework.pagination import BasePagination
from rest_framework.pagination import Response

class EndlessPagination(BasePagination):
    page_size = 20

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def to_html(self):
        pass

    def paginate_queryset(self, queryset, request, view=None):
        if 'created_at__gt' in request.query_params:
            # created_at__gt is used for pull-refresh.
            # For convenience, pull-refresh doesn't use pagination but use download and refresh all data.
            # For data haven't updated for a long time, we don't use pull-refresh style, but use download to update with the latest data.
            created_at__gt = request.query_params['created_at__gt']
            queryset = queryset.filter(created_at__gt=created_at__gt)
            self.has_next_page=False
            return queryset.order_by('-created_at')

        if 'created_at__lt' in request.query_params:
            created_at__lt = request.query_params['created_at__lt']
            queryset = queryset.filter(created_at__lt=created_at__lt)

        queryset = queryset.order_by('-created_at')[:self.page_size + 1]
        self.has_next_page = (len(queryset) > self.page_size)
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
                'has_next_page': self.has_next_page,
                'results': data,
        })