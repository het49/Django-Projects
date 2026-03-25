from rest_framework import serializers
from users.models import User
from event.models import UserInvites,BeerCheckIn
from beershop.models import UserFavourite,BeerDetail,Rating, CheckOutImage


class BeerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeerDetail
        fields = ('name',)


class UserFavouritiesSerializer(serializers.ModelSerializer):
    beer_shop= BeerDetailSerializer()
    class Meta:
        model = UserFavourite
        fields = ('id', 'beer_shop')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('get_full_name',)


class UserInvitesSerializer(serializers.ModelSerializer):
    invitee = UserDetailSerializer()

    class Meta:
        model = UserInvites
        fields = ('invitee', 'location','status')


class UserFeedbackSerializer(serializers.ModelSerializer):
    beer_shop = serializers.CharField(source="beer_shop.name")
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Rating
        fields = ('beer_shop','rating','feedback','created_at')

    def get_created_at(self,obj):
        return obj.created_at.strftime("%m/%d/%Y, %H:%M:%S")



class BeerCheckInImageSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    checkout_image = serializers.SerializerMethodField()

    class Meta:
        model = CheckOutImage
        fields = ('checkout_image','id')

    def get_checkout_image(self, obj):
        if obj.checkout_image:
            request = self.context.get('request')
            checkout_image = obj.checkout_image.url
            return request.build_absolute_uri(checkout_image)
        else:
            checkout_image = ""
            return checkout_image



