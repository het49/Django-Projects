from rest_framework.views import exception_handler
from collections import OrderedDict
from rest_framework import exceptions, status
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import PermissionDenied


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    message = _('Invalid input.')
    status = 4
    data = {}
    try:
        if isinstance(exc, exceptions.APIException):
            if isinstance(exc.detail, (list, dict)):
                message = exc.detail['messages'][0]['message']
            else:
                status = 4
                message = exc.detail
                data = {}

            # Now add the HTTP status code to the response.
            if response is not None:
                item_dict = OrderedDict()
                item_dict['status'] = status
                item_dict['message'] = message
                item_dict['data'] = data
                response.data = item_dict
        elif isinstance(exc, Http404):
            if response is not None:
                item_dict = OrderedDict()
                item_dict['status'] = 3
                item_dict['message'] = error_message
                item_dict['data'] = response.data
                response.data = item_dict

        elif isinstance(exc, PermissionDenied):
            if response is not None:
                item_dict = OrderedDict()
                item_dict['status'] = 3
                item_dict['message'] = error_message
                item_dict['data'] = response
                response.data = item_dict
    except:
        pass
    return response
