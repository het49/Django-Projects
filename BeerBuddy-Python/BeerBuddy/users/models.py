from django.db import models
from django.db.models import Avg
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django_mysql.models import JSONField
from django.utils.translation import gettext_lazy as _

from BeerBuddy.storage_backends import *


class Country(models.Model):
    code = models.CharField(max_length=10, null=True, blank=True)
    country_name = models.CharField(max_length=100, null=True, blank=True)
    flag = models.ImageField(storage=TestStorage(), blank=True, null=True)
    isd_code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.country_name

    class Meta:
        db_table = 'country'


class ContactList(models.Model):
    number = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    beer_buddy_user = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'contact_list'

# -----------------------
# -----------------------

def profile_upload_func(instance, filename):
    return f"profile/{filename}"

class User(AbstractUser):
    Types = (
        ('NORMALUSER','NORMALUSER'),
        ('BREWERY','BREWERY'),
        )
    SOURCE_TYPE_CHOICE = (
        ('normal', 'Normal'),
        ('social', 'Social'),
    )
    LOGIN_TYPE_CHOICE = (
        ('email', 'email'),
        ('phone_no', 'phone_no'),
    )
    GENDER_CHOICE = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    # What type of user are we?
    type = models.CharField(_("Type"), max_length=50, choices=Types, default="NORMALUSER")

    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=False, blank=False)
    contact = models.ManyToManyField(ContactList)
    phone_no = models.CharField(
        max_length=10, null=True, blank=True, unique=True)
    alternate_no = models.CharField(
        max_length=20, null=True, blank=True, unique=True)
    brewery_phone = models.CharField(
        max_length=10, null=True, blank=True)
    login_type = models.CharField(
        max_length=20, choices=LOGIN_TYPE_CHOICE, default="phone_no")
    #profile_img = models.ImageField(storage=TestStorage(), blank=True, null=True)
    profile_img = models.ImageField(storage=PublicMediaStorage(), upload_to=profile_upload_func, blank=True, null=True)
    source = models.CharField(
        max_length=30, choices=SOURCE_TYPE_CHOICE, default="normal")
    facebook_id = models.CharField(
        max_length=200, null=True, blank=True, unique=True)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICE)
    dob = models.DateField(null=True, blank=True)
    dob_visible = models.BooleanField(default=False)
    email_visible = models.BooleanField(default=False)
    contact_visible = models.BooleanField(default=False)
    notification_alert = models.BooleanField(default=True)
    longitude = models.FloatField(default=0.00)
    langitude = models.FloatField(default=0.00)
    address = models.CharField(max_length=200, default="", null=True, blank=True)
    brewery_name = models.CharField(max_length=50, default="",null=True, blank=True)
    place_id = models.CharField(max_length=50, default="",null=True, blank=True)
    brewery_desc = models.CharField(max_length=500, default="",null=True, blank=True)
    placedata = JSONField(null=True, blank=True)
    is_mobile_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'user'
        #ordering = ['created_at', 'updated_at']

    @property
    def is_email_login_type(self):
        return True if self.login_type in ["email"] else False

    @property
    def is_phone_login_type(self):
        return True if self.login_type in ["phone_no"] else False

    @property
    def is_user_active(self):
        return True if self.is_active in ["True"] else False


class UserFriend(models.Model):
    FRIEND_STATUS_CHOICE = (
        ('accepted', 'Accepted'),
        ('rejected', 'Declined'),
        ('pending', 'Pending'),
        ('cancel', 'Cancel'),
    )

    user = models.ForeignKey(
        User, related_name='requested_user', on_delete=models.CASCADE)
    friend = models.ForeignKey(
        User, related_name='friend_user', on_delete=models.CASCADE)
    location = models.CharField(max_length=80, null=True, blank=True)
    status = models.CharField(
        max_length=30, choices=FRIEND_STATUS_CHOICE, default="pending")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    read_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.friend.id)

    class Meta:
        db_table = 'user_friend'


class DeviceDetail(models.Model):
    PLATFORM_CHOICE = (
        ('android', 'android'),
        ('ios', 'ios'),
        ('unknown', 'unknown')
    )
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE)
    platform = models.CharField(
        max_length=30, choices=PLATFORM_CHOICE, default="unknown")
    device_token = models.TextField(null=True, blank=True)
    device_id = models.TextField(null=False, blank=False)
    app_version = models.CharField(max_length=20, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.platform

    class Meta:
        db_table = 'device_detail'
        ordering = ['-created_at', '-updated_at']

    def is_ios(self):
        return True if self.platform in ["ios"] else False

    def is_android(self):
        return True if self.platform in ["android"] else False


class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.id)

    class Meta:
        db_table = 'otp_verification'


class AppVersion(models.Model):
    PLATFORM_CHOICE = (
        ('android', 'android'),
        ('ios', 'ios'),
    )
    forcefull_version = models.CharField(
        max_length=10, null=False, blank=False)
    optional_version = models.CharField(max_length=10, null=False, blank=False)
    platform = models.CharField(
        max_length=20, choices=PLATFORM_CHOICE, default="android")

    def __str__(self):
        return str(self.forcefull_version)

    class Meta:
        db_table = 'app_version'
        ordering = ['-id']
    
