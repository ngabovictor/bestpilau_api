from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'pagination': {
                'count': self.page.paginator.count,
                'page_size': self.page.paginator.per_page,
                'page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
            },
            'results': data
        })
