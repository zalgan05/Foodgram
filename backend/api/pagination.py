from rest_framework.pagination import PageNumberPagination


class FollowPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'
