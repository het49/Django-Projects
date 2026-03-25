from django.db.models import Avg
from rest_framework import serializers
from users.models import User,UserFriend
from beershop.models import BeerDetail,UserFavourite,CheckOutImage,Rating
from event.models import BeerCheckIn


# Serializer for Country list
class BeerTypeSerializer(serializers.Serializer):
    name = serializers.CharField()


class GetBeerDetailSerializer(serializers.Serializer):
    id = serializers.CharField()


class BeerDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    geometry = serializers.JSONField()
    icon = serializers.CharField(required=False)
    google_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    place_id = serializers.CharField(required=False)
    plus_code = serializers.JSONField(required=False)
    photos = serializers.JSONField(required=False)
    reference = serializers.CharField(required=False)
    scope = serializers.CharField(required=False)
    types = BeerTypeSerializer(read_only=True, many=True)
    vicinity = serializers.CharField(required=False)
    formatted_address = serializers.CharField(required=False)

class BeerDetailRatingSerializer(serializers.Serializer):
    beerdetail = BeerDetailSerializer(read_only=True, many=True)
    favourite = serializers.CharField()
    rating =  serializers.CharField()

class BeerCheckInSerializer(serializers.Serializer):
    beer_id = serializers.CharField()
    check_in_status = serializers.CharField(required=False)


class UserFavouriteSerializer(serializers.Serializer):
    beer_id = serializers.CharField()
    status = serializers.BooleanField()


class GetUserFavouriteSerializer(serializers.ModelSerializer):
    beer_shop = BeerDetailSerializer(read_only=True)
    user = serializers.CharField(source="user.id")
    total_users_checkin = serializers.SerializerMethodField()
    users_checkin = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    checkout_images = serializers.SerializerMethodField()

    def get_total_users_checkin(self,obj):
        total_users_checkin = BeerCheckIn.objects.filter(beer = obj.beer_shop, status = True).exclude(user=self.context.get('request').user.id).count()
        return total_users_checkin

    def get_users_checkin(self,obj):
        users_checkin = BeerCheckIn.objects.filter(user = obj.user,beer=obj.beer_shop,status = True).order_by("-updated_at")
        if users_checkin.exists():
            return True
        else:
            return False

    def get_rating(self,obj):
        rating = Rating.objects.filter(beer_shop=obj.beer_shop).aggregate(Avg('rating'))['rating__avg']
        if rating is not None:
            rating = rating
        else:
            rating = 0
        return rating

    def get_checkout_images(self, obj):
        request = self.context.get('request')
        checkout_image =[]
        checkout_images = BeerCheckIn.objects.filter(beer = obj.beer_shop)
        for images in checkout_images:
            for image in images.images.all():
                checkout_image.append(request.build_absolute_uri(image.checkout_image.url))
        checkout_images_count = len(checkout_image)
        checkout_image.insert(0,checkout_images_count)
        return checkout_image

    class Meta:
        model = UserFavourite
        fields = ('beer_shop','user','total_users_checkin','users_checkin','rating','checkout_images','status')


class GetRatingSerializer(serializers.Serializer):
    user_id = serializers.CharField(source = "user.id")
    user_name = serializers.CharField(source = "user.get_full_name")
    user_phone_no = serializers.CharField(source = "user.phone_no")
    user_profile_img = serializers.SerializerMethodField()
    rating = serializers.FloatField(min_value = 0,max_value = 5)
    feedback = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(required = False)


    def get_feedback(self,obj):
        if obj.feedback != None:
            feedback = obj.feedback
        else:
            feedback = ""
        return feedback

    def get_user_profile_img(self,obj):

        if obj.user.profile_img:
            request = self.context.get('request')
            profile_img = obj.user.profile_img.url
            return request.build_absolute_uri(profile_img)


class RatingSerializer(serializers.Serializer):
    beer_id = serializers.CharField()
    rating = serializers.FloatField(min_value = 0,max_value = 5)
    feedback = serializers.CharField(required = False)
    images = serializers.ImageField(required = False)




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


class DashboardImageSerializer(serializers.Serializer):
    images = CheckoutImageSerializer(many=True)


class UserFriendSerializer(serializers.Serializer):
    friend = serializers.CharField()
    location = serializers.CharField(allow_blank=False, allow_null=False)
    status = serializers.CharField()

class BeerCheckOutSerializer(serializers.Serializer):
    beer_id = serializers.CharField()
    images = serializers.ImageField(required=False)

class GetUserFriendSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="friend.id")
    friend_name = serializers.CharField(source="friend.get_full_name")
    friend_number = serializers.CharField(source="friend.phone_no")
    sender = serializers.SerializerMethodField()
    friend_profile_img = serializers.SerializerMethodField()


    class Meta:
        model = UserFriend
        fields = ('id','friend_name','friend_number','status','sender','friend_profile_img','updated_at')

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


class GetUserFriendsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    friend_name = serializers.CharField(source="user.get_full_name")
    friend_number = serializers.CharField(source="user.phone_no")
    sender = serializers.SerializerMethodField()
    friend_profile_img = serializers.SerializerMethodField()


    class Meta:
        model = UserFriend
        fields = ('id','friend_name','friend_number','status','sender','friend_profile_img','updated_at')

    def get_sender(self, obj):
        return False

    def get_friend_profile_img(self, obj):
        if obj.friend.profile_img:
            request = self.context.get('request')
            profile_img = obj.user.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img


class GetUserContactSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.SerializerMethodField()
    phone_no = serializers.CharField()
    profile_img = serializers.SerializerMethodField()


    def get_name(self,obj):
        try:
            name = obj.first_name
        except:
            name = ""
        return name

    def get_profile_img(self, obj):
        if obj.profile_img:
            request = self.context.get('request')
            profile_img = obj.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img
