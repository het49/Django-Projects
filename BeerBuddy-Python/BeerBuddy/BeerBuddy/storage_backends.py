from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class TestStorage(S3Boto3Storage):
    location = settings.TEST_MEDIA_LOCATION
    default_acl = 'public-read'


class PublicMediaStorage(S3Boto3Storage):
    location = settings.PUBLIC_MEDIA_LOCATION
    default_acl = 'public-read'

# class ProfileMediaStorage(S3Boto3Storage):
# 	location = settings.PROFILE_MEDIA_LOCATION
# 	default_acl = 'public-read'

# class OffersMediaStorage(S3Boto3Storage):
# 	location = settings.OFFERS_MEDIA_LOCATION
# 	default_acl = 'public-read'