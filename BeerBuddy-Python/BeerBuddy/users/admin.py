from django.contrib import admin
from users.models import *


# Register your models here.


class UserAdmin(admin.ModelAdmin):

    list_display = ['id', 'username', 'first_name', 'phone_no',
                    'last_name', 'country', 'login_type', 'dob', 'is_active']
    search_fields = ['first_name', 'username']
    list_editable = ['is_active']
    list_per_page = 20

    
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'country_name',
                    'flag', 'isd_code', 'is_active']
    search_fields = ['code', 'country_name', 'isd_code']
    list_editable = ['is_active']
    list_per_page = 20


class DeviceDetailAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    list_display = [user, 'platform', 'device_id', 'app_version',
                    'access_token', 'refresh_token', 'created_at', 'updated_at']
    search_fields = ['user__username', 'platform', 'app_version']

    list_per_page = 20


class OTPVerificationAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    list_display = [user, 'otp', 'is_verified']
    search_fields = ['user__username']


class UserFriendAdmin(admin.ModelAdmin):
    def user(self):
        return self.user.username

    def friend(self):
        return self.friend.username

    list_display = [user, friend, 'location', 'status']
    search_fields = ['user__username', 'friend__username', 'location']
    list_per_page = 20


class ContactListAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'is_active', 'beer_buddy_user']
    search_fields = ['name', 'number', 'is_active', 'beer_buddy_user']
    list_per_page = 100


class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['forcefull_version', 'optional_version']
    search_fields = ['forcefull_version', 'optional_version']
    list_per_page = 10


admin.site.register(User, UserAdmin)
admin.site.register(DeviceDetail, DeviceDetailAdmin)
admin.site.register(OTPVerification, OTPVerificationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(UserFriend, UserFriendAdmin)


admin.site.register(ContactList, ContactListAdmin)
admin.site.register(AppVersion, AppVersionAdmin)

# admin.site.register(RatingImage)
