from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from . import custom_mixins
from rest_framework import exceptions, status
from collections import OrderedDict
from django.http import Http404
from django.core.exceptions import PermissionDenied


class CustomAPIView(APIView):
    success_message = None
    fail_message = 'Invalid input.'
    error_message = None

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        if isinstance(exc, (exceptions.NotAuthenticated,
                            exceptions.AuthenticationFailed)):
            # WWW-Authenticate header for 401 responses, else coerce to 403
            auth_header = self.get_authenticate_header(self.request)

            if auth_header:
                exc.auth_header = auth_header
            else:
                exc.status_code = status.HTTP_403_FORBIDDEN

        exception_handler = self.get_exception_handler()
        context = self.get_exception_handler_context()
        response = exception_handler(exc, context)
        message = None
        if response:
            if self.error_message is not None:
                message = self.error_message

            if response.data['status'] == 'fail':
                if self.fail_message is not None:
                    message = self.fail_message
            if message:
                response.data['message'] = message

        if response is None:
            self.raise_uncaught_exception(exc)

        response.exception = True
        return response


class CustomGenericAPIView(CustomAPIView, GenericAPIView):
    pass


class CreateAPIView(custom_mixins.CustomCreateModelMixin,
                    CustomGenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(custom_mixins.CustomListModelMixin,
                  CustomGenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):

        return self.list(request, *args, **kwargs)


class RetrieveAPIView(custom_mixins.CustomRetrieveModelMixin,
                      CustomGenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(custom_mixins.CustomDestroyModelMixin,
                     CustomGenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(custom_mixins.CustomUpdateModelMixin,
                    CustomGenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(custom_mixins.CustomListModelMixin,
                        custom_mixins.CustomCreateModelMixin,
                        CustomGenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(custom_mixins.CustomRetrieveModelMixin,
                            custom_mixins.CustomUpdateModelMixin,
                            CustomGenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(custom_mixins.CustomRetrieveModelMixin,
                             custom_mixins.CustomDestroyModelMixin,
                             CustomGenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(custom_mixins.CustomRetrieveModelMixin,
                                   custom_mixins.CustomUpdateModelMixin,
                                   custom_mixins.CustomDestroyModelMixin,
                                   CustomGenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
