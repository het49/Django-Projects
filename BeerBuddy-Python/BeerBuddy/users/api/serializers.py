from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from users.models import *

User = get_user_model()

# Serializer for Country list
class CountrySerializer(serializers.ModelSerializer):
    flag = serializers.SerializerMethodField()
    class Meta:
        model = Country
        fields = ['id','code','country_name','flag','isd_code']
    def get_flag(self,country):
        request = self.context.get('request')
        flag = country.flag.url
        return request.build_absolute_uri(flag)


class UserCreateSerializer(serializers.Serializer):
    login_type = serializers.CharField()
    country_code = serializers.CharField(required=False)
    phone_no = serializers.CharField(
        min_length=10, max_length=12, required=False)
    password = serializers.CharField(min_length=8,write_only=True)
    dob = serializers.DateField()
    email = serializers.CharField(max_length=100)



class UserVerifyPasscodeSerializer(serializers.Serializer):
    country_code = serializers.CharField(required=False)
    phone_no = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)
    passcode = serializers.CharField(write_only=True)


class UserLoginSerializer(serializers.Serializer):
    country_code = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    login_type = serializers.CharField()
    social_id = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(required=False,min_length=8, write_only=True)

class UserLogoutSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)


class GetImageSerializer(serializers.Serializer):
    profile_img = serializers.SerializerMethodField()

    def get_profile_img(self, obj):
        if obj.profile_img:
            request = self.context.get('request')
            profile_img = obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img


class ForgotPasswordSerializer(serializers.Serializer):
    country_code = serializers.CharField(required=False)
    phone_no = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)

class VerifyForgotPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    country_code = serializers.CharField(required=False)
    phone_no = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(required=False, allow_null=True)


class ResetPasswordSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only = True)
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8,write_only=True)


class GetProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField()
    phone_no = serializers.SerializerMethodField()
    email_visible = serializers.BooleanField()
    phone_no_visible = serializers.BooleanField(source="contact_visible")
    dob_visible = serializers.BooleanField()
    gender = serializers.CharField()
    dob = serializers.DateField()
    profile_img = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_name(self,obj):
        try:
            if obj.last_name !="":
                name = obj.first_name + " " + obj.last_name
            else:
                name = obj.first_name
        except:
            name = ""
        return name

    def get_profile_img(self,obj):
        if obj.profile_img:
            request = self.context.get('request')
            profile_img = obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_city(self,obj):
        if obj.city != None:
            city = obj.city
        else:
            city = ""
        return city

    def get_state(self,obj):
        if obj.state != None:
            state = obj.state
        else:
            state = ""
        return state

    def get_phone_no(self, obj):
        try:
            if obj.phone_no:
                return obj.phone_no
            return ""
        except:
            return ""


class UpdateProfileSerializer(serializers.Serializer):

    name = serializers.CharField()
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.CharField()
    email = serializers.EmailField()
    city = serializers.CharField()
    state = serializers.CharField()
    profile_img = serializers.ImageField(required=False)
    phone_no = serializers.CharField(
        min_length=10, max_length=12, required=False)


class AddContactListSerializer(serializers.Serializer):
    number = serializers.CharField()
    name = serializers.CharField()


#### code customize #######

class ContactListSerializer(serializers.Serializer):
    user_id = serializers.SerializerMethodField()
    number = serializers.CharField()
    name = serializers.CharField()
    beer_buddy_user = serializers.CharField()
    is_connected = serializers.SerializerMethodField()
    is_sender = serializers.SerializerMethodField()
    contact_profile_img = serializers.SerializerMethodField()

    def get_user_id(self, obj):
        user_obj = User.objects.get(phone_no=obj.number)
        return user_obj.id

    def get_is_sender(self,obj):
        friend_obj = User.objects.get(phone_no=obj.number)
        friend_users = UserFriend.objects.filter(Q(user=self.context.get('request').user, friend=friend_obj) |Q(friend=self.context.get('request').user, user=friend_obj) ).order_by("-created_at")
        if friend_users.exists():
            if friend_users[0].user == self.context.get('request').user:
                return 1
            else:
                return 2
        else:
            return 0


    def get_is_connected(self, obj):
        friend_obj = User.objects.get(phone_no=obj.number)
        friend_users = UserFriend.objects.filter(Q(user=self.context.get('request').user, friend=friend_obj) |Q(friend=self.context.get('request').user, user=friend_obj) ).order_by("-created_at")

        if friend_users.exists():
            if friend_users[0].status == "accepted":
                return 1
            elif friend_users[0].status == "rejected":
                return 2
            elif friend_users[0].status == "pending":
                return 3
            elif friend_users[0].status == "cancel":
                return 4
        else:
            return 5

    def get_contact_profile_img(self, obj):

        user_obj = User.objects.get(phone_no=obj.number)

        if user_obj.profile_img:
            request = self.context.get('request')
            profile_img = user_obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img


### Access ReGenerate ######
class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(allow_blank = False,allow_null = False)

class GetAccessTokenSerializer(serializers.Serializer):
    id = serializers.CharField(source="user.id", read_only=True)
    platform = serializers.CharField(read_only=True)
    device_token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)


class CheckoutImageSerializer(serializers.Serializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.checkout_image:
            request = self.context.get('request')
            image = obj.checkout_image.url
            return request.build_absolute_uri(image)
        else:
            image = ""
            return image


class UserFriendSerializer(serializers.Serializer):
    friend = serializers.CharField()
    status = serializers.CharField()


class GetUserFriendSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="friend.id")
    friend_name = serializers.CharField(source="friend.get_full_name")
    friend_number = serializers.SerializerMethodField()
    friend_city = serializers.SerializerMethodField()
    friend_state = serializers.SerializerMethodField()
    friend_phone_visible = serializers.BooleanField(source="friend.contact_visible")
    sender = serializers.SerializerMethodField()
    friend_profile_img = serializers.SerializerMethodField()
    friend_email = serializers.SerializerMethodField()


    class Meta:
        model = UserFriend
        fields = ('id', 'friend_name', 'friend_number', 'friend_city', 'friend_state',
                  'friend_phone_visible', 'status', 'sender', 'friend_profile_img', 'updated_at', 'friend_email')

    def get_sender(self, obj):
        return True

    def get_friend_profile_img(self, obj):
        if obj.friend.profile_img:
            request = self.context.get('request')
            profile_img = obj.friend.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_friend_city(self, obj):
        if obj.friend.city:
            return obj.friend.city
        else:
            city = ""
            return city

    def get_friend_state(self, obj):
        if obj.friend.state:
            return obj.friend.state
        else:
            state = ""
            return state
    
    def get_friend_number(self, obj):
        if obj.friend.phone_no:
            return obj.friend.phone_no
        return ""

    def get_friend_email(self, obj):
        if obj.friend.email:
            return obj.friend.email
        return ""

class GetUserFriendsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    friend_name = serializers.CharField(source="user.get_full_name")
    friend_number = serializers.SerializerMethodField()
    friend_city = serializers.SerializerMethodField()
    friend_state = serializers.SerializerMethodField()
    friend_phone_visible = serializers.BooleanField(source="user.contact_visible")
    sender = serializers.SerializerMethodField()
    friend_profile_img = serializers.SerializerMethodField()
    friend_email = serializers.SerializerMethodField()


    class Meta:
        model = UserFriend
        fields = ('id', 'friend_name', 'friend_number', 'friend_city', 'friend_state',
                  'friend_phone_visible', 'status', 'sender', 'friend_profile_img', 'updated_at', 'friend_email')

    def get_sender(self, obj):
        return False

    # def get_id(self, obj):
    # request = self.context.get('request')
    #     if obj.user == request.user:
    #         return obj.user.id
    #     elif obj.friend == request.user:
    #         return obj.friend.id
    #
    def get_friend_profile_img(self, obj):
        if obj.user.profile_img:
            request = self.context.get('request')
            profile_img = obj.user.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_friend_city(self, obj):
        if obj.user.city:
            return obj.user.city
        else:
            city = ""
            return city

    def get_friend_state(self, obj):
        if obj.user.state:
            return obj.user.state
        else:
            state = ""
            return state

    def get_friend_number(self, obj):
        if obj.user.phone_no:
            return obj.user.phone_no
        return ""
    
    def get_friend_email(self, obj):
        if obj.user.email:
            return obj.user.email
        return ""


class SocialPhoneUpdateSerializer(serializers.Serializer):
    country_code = serializers.CharField()
    phone_no = serializers.CharField(min_length=10,max_length=12)


class SocialVerifyPasscodeSerializer(serializers.Serializer):
    country_code = serializers.CharField()
    phone_no = serializers.CharField(allow_blank=False, allow_null=False)
    passcode = serializers.CharField(write_only=True)


class SearchSerializer(serializers.Serializer):
    id = serializers.CharField()
    phone = serializers.SerializerMethodField()
    phone_visible = serializers.BooleanField(source = "contact_visible")
    name = serializers.CharField(source = "get_full_name")
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    is_connected = serializers.SerializerMethodField()
    is_sender = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        if obj.email:
            return obj.email
        return ""

    def get_phone(self,obj):
        if obj.phone_no:
            return obj.phone_no
        else:
            return ""

    def get_city(self, obj):
        if obj.city:
            return obj.city
        else:
            city = ""
            return city

    def get_state(self,obj):
        if obj.state:
            return obj.state
        else:
            state = ""
            return state

    def get_profile_img(self, obj):
        if obj.profile_img:
            request = self.context.get('request')
            profile_img = obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_is_sender(self,obj):
        friend_users = UserFriend.objects.filter(Q(user=self.context.get('request').user, friend=obj) |Q(friend=self.context.get('request').user, user=obj) ).order_by("-created_at")
        if friend_users.exists():
            if friend_users[0].user == self.context.get('request').user:
                return 1
            else:
                return 2
        else:
            return 0


    def get_is_connected(self, obj):
        # friend_obj = User.objects.get(phone_no=obj.number)
        friend_users = UserFriend.objects.filter(Q(user=self.context.get('request').user, friend=obj)|Q(friend=self.context.get('request').user, user=obj)).order_by("-created_at")

        if friend_users.exists():
            if friend_users[0].status == "accepted":
                return 1
            elif friend_users[0].status == "rejected":
                return 2
            elif friend_users[0].status == "pending":
                return 3
            elif friend_users[0].status == "cancel":
                return 4
        else:
            return 5

class SettingSerializer(serializers.Serializer):
    setting_key = serializers.CharField()

class GetOtherProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()
    email = serializers.EmailField()
    email_visible = serializers.BooleanField()
    phone_no_visible = serializers.BooleanField(source="contact_visible")
    dob_visible = serializers.BooleanField()
    phone_no = serializers.SerializerMethodField()
    gender = serializers.CharField()
    dob = serializers.DateField()
    profile_img = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    def get_name(self,obj):
        try:
            if obj.last_name !="":
                name = obj.first_name + " " + obj.last_name
            else:
                name = obj.first_name
        except:
            name = ""
        return name

    def get_profile_img(self,obj):
        if obj.profile_img:
            request = self.context.get('request')
            profile_img = obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_city(self,obj):
        if obj.city != None:
            city = obj.city
        else:
            city = ""
        return city

    def get_state(self,obj):
        if obj.state != None:
            state = obj.state
        else:
            state = ""
        return state
    
    def get_phone_no(self, obj):
        if obj.phone_no != None:
            return obj.phone_no
        return ""


class ResentOTPSerializer(serializers.Serializer):
    requested_type = serializers.CharField()
    username = serializers.CharField(required=False, allow_blank=True)
    phone_no = serializers.CharField(required=False, allow_blank=True)
    country_code = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_null=True)


class AppVersionSerializer(serializers.Serializer):
    forcefull_version = serializers.CharField(required=False, allow_blank=True)
    optional_version = serializers.CharField(required=False, allow_blank=True)
