from rest_framework import serializers
from users.models import User, ContactList, UserFriend
from brewery.models import Brewery

class GetUserFriendSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="friend.id")
    friend_name = serializers.CharField(source="friend.get_full_name")
    friend_number = serializers.CharField(source="friend.phone_no")

    class Meta:
        model = UserFriend
        fields = ('id','friend_name','friend_number')

class GetUserFriendsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    friend_name = serializers.CharField(source="user.get_full_name")
    friend_number = serializers.CharField(source="user.phone_no")


    class Meta:
        model = UserFriend
        fields = ('id','friend_name','friend_number')


# class ContactListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ContactList
#         fields = ('name','number')


class UserDetailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',  'phone_no', 'dob', 'gender', 'city','state')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('get_full_name',)
# ========================================================================================
class BreweryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brewery
        fields = ("login_type","phone_no","email")
        extra_kwargs = {'phone_no': {'validators': []},}

class BreweryProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brewery
        fields = ('longitude','langitude','address','brewery_name','profile_img','brewery_desc','place_id','first_name','last_name','placedata')


