from rest_framework import pagination
class StandardResultsSetPagination1(pagination.PageNumberPagination):
    page_size = 4 # change the records per page from here

    page_size_query_param = 'page_size'