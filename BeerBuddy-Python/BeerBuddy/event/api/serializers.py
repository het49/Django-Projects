from rest_framework import exceptions
from rest_framework import serializers
from users.models import User
from event.models import UserInvites,BeerCheckIn,EventComments
from beershop.models import BeerDetail,CheckOutImage,Rating
from django.db.models import Avg
from beershop.api.serializers import BeerDetailSerializer
from pytz import timezone
from base.utils.utilities import get_beer_detail,get_checkout_img,get_avg_rating,get_favourite
from datetime import timedelta


class GetUserInvitesSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="invitee.id")
    invitee_name = serializers.CharField(source="invitee.get_full_name")
    invitee_number = serializers.CharField(source="invitee.phone_no")
    invitee_number_visible = serializers.CharField(source="invitee.contact_visible")
    invitee_profile_img = serializers.SerializerMethodField()
    beer_shop_id = serializers.CharField(source="event.beer_shop.id")
    beer_shop_google_id = serializers.CharField(source="event.beer_shop.google_id")
    beer_shop_place_id = serializers.CharField(
        source="event.beer_shop.place_id")
    beer_shop_name = serializers.CharField(source="event.beer_shop.name")
    event_id = serializers.CharField(source="event.id")
    sender = serializers.SerializerMethodField()

    class Meta:
        model = UserInvites
        fields = ('beer_shop_id','beer_shop_google_id','beer_shop_name','id','invitee_name','invitee_number','invitee_number_visible','invitee_profile_img','status','event_id','sender','updated_at')

    def get_sender(self,obj):
        return True

    def get_invitee_profile_img(self, obj):
        if obj.invitee.profile_img:
            request = self.context.get('request')
            profile_img = obj.invitee.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img


class GetUserInvitedSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    invitee_name = serializers.CharField(source="user.get_full_name")
    invitee_number = serializers.CharField(source="user.phone_no")
    invitee_number_visible = serializers.CharField(source="user.contact_visible")
    invitee_profile_img = serializers.SerializerMethodField()
    beer_shop_id = serializers.CharField(source="event.beer_shop.id")
    beer_shop_google_id = serializers.CharField(source="event.beer_shop.google_id")
    beer_shop_name = serializers.CharField(source="event.beer_shop.name")
    event_id = serializers.CharField(source="event.id")
    sender = serializers.SerializerMethodField()


    class Meta:
        model = UserInvites
        fields = ('beer_shop_id','beer_shop_google_id','beer_shop_name','id','invitee_name','invitee_number','invitee_number_visible','invitee_profile_img','status','event_id','sender','updated_at')

    def get_sender(self,obj):
        return False

    def get_invitee_profile_img(self, obj):
        if obj.user.profile_img:
            request = self.context.get('request')
            profile_img = obj.user.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

class InvitiesUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
    event_id = serializers.CharField()

class InvitiesSerializer(serializers.Serializer):
    beer_shop = serializers.CharField()
    invitee = serializers.ListField(child=serializers.CharField())
    location = serializers.CharField( allow_blank=True, allow_null=True )
    message = serializers.CharField( allow_blank=True, allow_null=True )
    status = serializers.CharField()


class GetUserInvitedEventSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()
    phone_no = serializers.SerializerMethodField()
    phone_no_visible = serializers.SerializerMethodField()
    is_accepted = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_comment_count(self, obj):
        try:
            event_count = EventComments.objects.filter(event=obj.event).count()
        except:
            event_count = 0
        return event_count

    def get_phone_no_visible(self,obj):
        return obj.invitee.contact_visible



    def get_profile_img(self, obj):
        if obj.invitee.profile_img:
            request = self.context.get('request')
            profile_img = obj.invitee.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_id(self,obj):
        return obj.invitee.id


    def get_name(self,obj):
        return obj.invitee.first_name


    def get_phone_no(self,obj):
        return obj.invitee.phone_no


    def get_email(self, obj):
        return obj.invitee.email


    def get_is_accepted(self,obj):
        users_checkin = BeerCheckIn.objects.filter(user=obj.invitee, event=obj.event, beer=obj.event.beer_shop)
        if obj.status == "accepted":
            if users_checkin.exists():
                if users_checkin[0].status == True:
                    return 6
                else:
                    return 7
            else:
                return 1
        elif obj.status == "rejected":
            return 2
        elif obj.status == "pending":
            return 3
        elif obj.status == "cancel":
            return 4
        else:
            return 5

class GetUserInviteeEventSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()
    phone_no = serializers.SerializerMethodField()
    phone_no_visible = serializers.SerializerMethodField()
    is_accepted = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()


    def get_comment_count(self,obj):
        try:
            event_count = EventComments.objects.filter(event=obj.event).count()
        except:
            event_count = 0
        return event_count


    def get_phone_no_visible(self, obj):
        return obj.user.contact_visible

    def get_profile_img(self, obj):
        if obj.user.profile_img:
            request = self.context.get('request')
            profile_img = obj.user.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_id(self, obj):
        return obj.user.id

    def get_name(self, obj):
        return obj.user.first_name

    def get_phone_no(self, obj):
        return obj.user.phone_no

    def get_is_accepted(self, obj):
        users_checkin = BeerCheckIn.objects.filter(user=obj.user, event=obj.event, beer=obj.event.beer_shop)
        if obj.status == "accepted":
            if users_checkin.exists():
                if users_checkin[0].status == True:
                    return 6
                else:
                    return 7
            else:
                return 1
        elif obj.status == "rejected":
            return 2
        elif obj.status == "pending":
            return 3
        elif obj.status == "cancel":
            return 4
        else:
            return 5




class EventListingSender(serializers.Serializer):
    date = serializers.SerializerMethodField()
    event_id = serializers.CharField(source = "id")
    beer_shop = serializers.SerializerMethodField()
    event_owner = serializers.SerializerMethodField()
    users_checkin = serializers.SerializerMethodField()
    checkout_images = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_rated = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    is_title_show = serializers.SerializerMethodField()

    def get_users_checkin(self,obj):
        user_obj = self.context.get('user_obj')
        users_checkin = BeerCheckIn.objects.filter(user=user_obj, event=obj, beer=obj.beer_shop)
        if users_checkin.exists():
            if users_checkin[0].status == True:
                return  0
            else:
                return 2
        else:
            return 1
    def get_is_title_show(self,obj):
        return False


    def get_beer_shop(self,obj):
        return get_beer_detail(obj.beer_shop)

    def get_message(self,obj):
       return obj.event_invites.all()[0].message if obj.event_invites.all() else ""

    def get_is_favourite(self,obj):
        user_obj = self.context.get('user_obj')
        return get_favourite(user_obj,obj.beer_shop)

    def get_event_owner(self,obj):
        return True

    def get_rating(self,obj):
        return get_avg_rating(obj.beer_shop)

    def get_is_rated(self, obj):
        is_rated = False
        user_obj = self.context.get('user_obj')
        if Rating.objects.filter(beer_shop = obj.beer_shop, user = user_obj).exists():
            is_rated = True
        return is_rated

    def get_date(self,obj):
        time_diff = self.context.get('time_diff')
        date_obj = obj.created_at + timedelta(minutes=time_diff)
        return date_obj.replace(tzinfo=timezone('UTC'))

    def get_checkout_images(self,obj):
        request = self.context.get('request')
        return get_checkout_img(request,obj.beer_shop)

class EventListingRecevied(serializers.Serializer):
    date = serializers.SerializerMethodField()
    event_id = serializers.CharField(source = "event.id")
    beer_shop = serializers.SerializerMethodField()
    event_owner = serializers.SerializerMethodField()
    users_checkin = serializers.SerializerMethodField()
    checkout_images = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_rated = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    is_title_show = serializers.SerializerMethodField()

    def get_users_checkin(self,obj):
        user_obj = self.context.get('user_obj')
        users_checkin = BeerCheckIn.objects.filter(user=user_obj, event=obj.event, beer=obj.event.beer_shop)
        if users_checkin.exists():
            if users_checkin[0].status == True:
                return  0
            else:
                return 2
        else:
            return 1
    def get_is_title_show(self,obj):
        return False
    def get_beer_shop(self,obj):
        return get_beer_detail(obj.event.beer_shop)

    def get_message(self,obj):
       return obj.message if obj.message else ""
    def get_is_favourite(self,obj):
        user_obj = self.context.get('user_obj')
        return get_favourite(user_obj,obj.event.beer_shop)

    def get_event_owner(self,obj):
        return False

    def get_rating(self,obj):
        return get_avg_rating(obj.event.beer_shop)

    def get_is_rated(self, obj):
        is_rated = False
        user_obj = self.context.get('user_obj')
        if Rating.objects.filter(beer_shop = obj.event.beer_shop, user = user_obj).exists():
            is_rated = True
        return is_rated

    def get_date(self,obj):
        time_diff = self.context.get('time_diff')
        date_obj = obj.created_at + timedelta(minutes=time_diff)
        return date_obj.replace(tzinfo=timezone('UTC'))

    def get_checkout_images(self,obj):
        request = self.context.get('request')
        return get_checkout_img(request,obj.event.beer_shop)


class EventCommentsSerializer(serializers.Serializer):
    event_id = serializers.CharField()
    message = serializers.CharField()

class GetEventCommentsSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    is_current_user = serializers.SerializerMethodField()
    message = serializers.CharField()
    # created_at = serializers.CharField()


    class Meta:
        model = EventComments
        exclude = ("sender","event","updated_at")

    def get_user_id(self, obj):
        return obj.sender.id

    def get_user_name(self,obj):
        try:
            name = obj.sender.get_full_name()
        except:
            name = ""
        return name

    def get_user_image(self,obj):
        request = self.context.get("request")
        try:
            image = request.build_absolute_uri(obj.sender.profile_img.url)
        except:
            image = ""
        return image

    def get_is_current_user(self,obj):
        request =  self.context.get("request")
        is_current = False
        if obj.sender == request.user:
            is_current = True
        return is_current
