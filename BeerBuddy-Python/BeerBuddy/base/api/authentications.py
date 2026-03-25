from django.utils.translation import ugettext_lazy as _
from rest_framework_simplejwt.authentication import (JWTAuthentication,
                                                     AuthenticationFailed,
                                                     User, api_settings)
from ..exceptions.exceptions import LoginTimeOutError


class JWTCustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return (self.get_user_obj(request, validated_token), None)

    def get_user_obj(self, request, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        token = request.META.get('HTTP_AUTHORIZATION').split()[1]
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed(_('Token contained no recognizable user identification'))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'))

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'))
        if not user.devicedetail_set.filter(access_token=token).exists():
            raise LoginTimeOutError(_('User session has expired and must log in again.'))

        return user
