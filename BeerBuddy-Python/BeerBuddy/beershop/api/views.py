from rest_framework import generics
from django.core.exceptions import *
from rest_framework.permissions import (
    AllowAny, )
from rest_framework.response import Response
from rest_framework.views import APIView
from users.api.permissions import IsAllowed
from users.models import User,UserFriend
from notification.models import Message
from django.db.models import Q
from event.models import UserInvites,Event,BeerCheckIn
from notification.models import Notification
from beershop.models import BeerType, BeerDetail,UserFavourite,CheckOutImage,Rating,BeerPlacesDetail,ConfigParam
from beershop.api.serializers import (GetBeerDetailSerializer,BeerDetailSerializer,GetUserContactSerializer,BeerCheckInSerializer,RatingSerializer,GetRatingSerializer,
BeerCheckOutSerializer,CheckoutImageSerializer,GetUserFriendSerializer,GetUserFavouriteSerializer,UserFavouriteSerializer)
from base.utils.utilities import (validate_headers,error_response,success_response,save_beer_detail_json,get_favourite,get_user_check_in,
                                  get_total_users_check_in,get_avg_rating,create_notification,send_notification, haversine, get_beer_detail)
# ====================
from brewery.models import Brewery, Offer
import json



class AddBeerDetailAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):

        data = request.data
        print("a-------",data)
        serializer = GetBeerDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            id = data["id"]

            try:
                beerdetail_obj = BeerDetail.objects.get(place_id=id)

            except:
                message = "Beer Detail is not available with us."
                return_data = {}
                return error_response(message, return_data)


        serializers = BeerDetailSerializer(beerdetail_obj)
        message = "success"
        return_data = serializers.data
        print(return_data,"aaaa")
        return success_response(message, return_data)


    def post(self,request,*args,**kwargs):
        data = request.data
        print("beer===>",data)
        return_data = {}
        beerdetails = []
        for item in data:
            print(item,"item")
            id = save_beer_detail_json(item)
            if id == None:
                message = "Something went Wrong"
                return error_response(message, return_data)
            if isinstance(id, str):
                beershopdetail = BeerDetail.objects.get(place_id=id)
                print("ADD BEER", beershopdetail)
            else:
                beershopdetail = BeerDetail.objects.get(brewery=id)
                print("ADD brewery", beershopdetail)
            user_obj = request.user
            favourite = get_favourite(user_obj, beershopdetail)
            rating = get_avg_rating(beershopdetail)
            total_users_check_in = get_total_users_check_in(beershopdetail,user_obj.id)
            print("total",total_users_check_in)
            user_check_in = get_user_check_in(user_obj,beershopdetail)
            beer_checkin = BeerCheckIn.objects.filter(beer=beershopdetail).order_by("-updated_at")
            if beer_checkin.exists():
                images_list = []
                for images in beer_checkin:
                    images = CheckoutImageSerializer(images.images, many = True,context={'request': request})
                    for image in images.data:
                        images_list.append(image['image'])
                images_count = len(images_list)
                images_list.insert(0,images_count)
            else:
                images_list =[]

            beerdetail = {
                "beer_shop_id": beershopdetail.id,
                "beer_shop_name": beershopdetail.name,
                "beer_shop_google_id": beershopdetail.google_id,
                "beer_shop_place_id": beershopdetail.place_id,
                "total_users_checkin": total_users_check_in,
                "rating": rating,
                "favorite": favourite,
                "user_check_in":user_check_in,
                "checkout_images":images_list
            }
            friend_obj = user_obj.requested_user.filter(status="accepted")
            user_info_list = []
            if friend_obj.exists():
                for friends in friend_obj:
                    beer_check_in = BeerCheckIn.objects.filter(user = friends.friend,beer = beershopdetail,status = True)
                    if beer_check_in.exists():
                        serializer = GetUserContactSerializer(friends.friend, context={'request': request})
                        user_info = serializer.data
                        user_info_list.append(user_info)

            friend_obj = user_obj.friend_user.filter(status="accepted")
            if friend_obj.exists():
                for friends in friend_obj:
                    beer_check_in = BeerCheckIn.objects.filter(user = friends.user,beer = beershopdetail,status = True)
                    if beer_check_in.exists():
                        serializer = GetUserContactSerializer(friends.user, context={'request': request})
                        user_info = serializer.data
                        user_info_list.append(user_info)

            beerdetail["user_contact_list"] = user_info_list
            beerdetail["user_contact_list_length"] = len(user_info_list)
            beerdetails.append(beerdetail)
        return_data = {"beershopdetails": sorted(beerdetails, key=lambda k: k['user_contact_list_length'], reverse=True)}
        message = "success"
        print("beer end")
        return success_response(message,return_data)



class BeerCheckInAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args, **kwargs):
        data = request.data
        print("checkin",data)
        serializer = BeerCheckInSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            beer_id = data["beer_id"]
            user_timestamp = data.get("user_timestamp")
            print(user_timestamp,"STAMP")
            # event_id = data["event_id"]
            user_obj = request.user

            try:
                beerdetail_obj = BeerDetail.objects.get(id=beer_id)
            except:
                message = "Beer Detail is not available with us."
                return error_response(message, return_data)
            beercheckin_obj = BeerCheckIn.objects.filter(user=user_obj, status=True)
            if not beercheckin_obj.exists():
                user_invited = UserInvites.objects.filter(invitee=user_obj, event__beer_shop=beerdetail_obj,event__is_active=True, event__is_delete=False)
                user_invitee = UserInvites.objects.filter(user=user_obj, event__beer_shop=beerdetail_obj,event__is_active=True, event__is_delete=False)
                if user_invitee.exists():
                    beercheck_obj = BeerCheckIn.objects.create(user=user_obj, event=user_invitee[0].event,
                                                               beer=beerdetail_obj, status=True,
                                                               user_timestamp=user_timestamp)

                    for user_invite_obj in user_invitee:
                        if user_invite_obj.status != "accepted":
                            continue
                        receiver_obj = user_invite_obj.invitee
                        sender_obj = user_obj
                        sender_id = user_obj.id
                        sender_profile = request.build_absolute_uri(
                            user_obj.profile_img.url) if user_obj.profile_img else ""
                        obj_id = user_invite_obj.event.id
                        notification_type = 2  ### checkin type ####
                        try:
                            message_obj = Message.objects.get(title="checkin", type="other")
                            message = message_obj.text_message.format(username=sender_obj.first_name,
                                                                      beershop=beerdetail_obj.name)
                            message_title = message_obj.message_title
                            notification_id = create_notification(sender_obj,receiver_obj,message,obj_id,title_base ="checkin",type_base = "other",title_user = message_title,
                                                                  checkin_id=0,status = "unread",user_status = "")
                            print("created1")
                            send_notification(receiver_obj, notification_id, notification_type, message, message_title,sender_profile, sender_id,str(obj_id))
                            print("send")
                        except:
                            pass


                if user_invited.exists():
                    beercheck_obj = BeerCheckIn.objects.create(user=user_obj, event=user_invited[0].event,
                                                               beer=beerdetail_obj, status=True,
                                                               user_timestamp=user_timestamp)
                    for user_invite_obj in user_invited:
                        if user_invite_obj.status != "accepted":
                            continue
                        receiver_obj = user_invite_obj.user
                        sender_obj = user_obj
                        sender_id = user_obj.id
                        sender_profile = request.build_absolute_uri(
                            user_obj.profile_img.url) if user_obj.profile_img else ""
                        obj_id = user_invite_obj.event.id
                        notification_type = 2  ### checkin type ####
                        try:
                            message_obj = Message.objects.get(title="checkin", type="other", is_active=True)
                            message = message_obj.text_message.format(username=sender_obj.first_name,
                                                                      beershop=beerdetail_obj.name)
                            message_title = message_obj.message_title
                            notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                                                                  title_base="checkin", type_base="other",
                                                                  title_user=message_title,checkin_id=0,
                                                                  status="unread", user_status="")
                            print("created2")
                            send_notification(receiver_obj, notification_id, notification_type, message, message_title,
                                              sender_profile, sender_id, str(obj_id))

                        except:
                            pass

                        # event_invite = UserInvites.objects.filter(user = user_invite_obj.user,event__beer_shop=beerdetail_obj,event__is_active=True, event__is_delete=False,status = "accepted").exclude(invitee=user_obj)
                        # if event_invite.exists():
                        #     for invite_obj in event_invite:
                        #         receiver_obj = invite_obj.invitee
                        #         sender_obj = user_obj
                        #         sender_id = user_obj.id
                        #         sender_profile = request.build_absolute_uri(
                        #             user_obj.profile_img.url) if user_obj.profile_img else ""
                        #         obj_id = user_invite_obj.event.id
                        #         notification_type = 2  ### checkin type ####
                        #         try:
                        #             message_obj = Message.objects.get(title="checkin", type="other",is_active = True)
                        #             message = message_obj.text_message.format(username=sender_obj.first_name,
                        #                                                       beershop=beerdetail_obj.name)
                        #             message_title = message_obj.message_title
                        #             notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                        #                                                   title_base="checkin", type_base="other",title_user=message_title,status="unread", user_status="")
                        #             send_notification(receiver_obj, notification_id, notification_type, message,
                        #                               message_title,sender_profile, sender_id,str(obj_id))
                        #         except:
                        #             pass

                if (not user_invited.exists()) and  (not user_invitee.exists()):
                    new_event_obj = Event.objects.create(name=beerdetail_obj.name, created_by=user_obj,
                                                         beer_shop=beerdetail_obj)
                    beercheck_obj = BeerCheckIn.objects.create(
                        user=user_obj, event=new_event_obj, beer=beerdetail_obj, status=True, user_timestamp=user_timestamp)
                    sender_obj = user_obj
                    sender_id = user_obj.id
                    sender_profile = request.build_absolute_uri(
                        user_obj.profile_img.url) if user_obj.profile_img else ""
                    obj_id = new_event_obj.id
                    print("OBJ_ID",obj_id)
                    user_friend = UserFriend.objects.filter(user=user_obj, status="accepted")
                    # print("FRIEND",user_friend)
                    user_accepted_friend = UserFriend.objects.filter(friend=user_obj, status="accepted")

                    if user_friend.exists():
                        print("inside")
                        for friend_obj in user_friend:
                            print(friend_obj)
                            receiver_obj = friend_obj.friend
                            try:
                                message_obj = Message.objects.get(title="checkin", type="other")
                                message = message_obj.text_message.format(username=sender_obj.first_name,
                                                                          beershop=beerdetail_obj.name)
                                message_title = message_obj.message_title
                                notification_type = 2  ### checkin type ####
                    
                                notification_id = create_notification(sender_obj, receiver_obj, message,obj_id,
                                                                      title_base="checkin", type_base="other",
                                                                      title_user=message_title, checkin_id=beercheck_obj.id,status="unread",user_status="")
                                print("created3")

                                send_notification(receiver_obj, notification_id, notification_type,
                                                  message, message_title, sender_profile, sender_id, str(obj_id))
                            except Exception as e:
                                print(e)

                    if user_accepted_friend.exists():
                        for friend_obj in user_accepted_friend:
                            receiver_obj = friend_obj.user
                            try:
                                message_obj = Message.objects.get(title="checkin", type="other")
                                message = message_obj.text_message.format(username=sender_obj.first_name,
                                                                          beershop=beerdetail_obj.name)
                                message_title = message_obj.message_title
                                notification_type = 2  ### checkin type ####
                                notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                                                                      title_base="checkin", type_base="other",
                                                                      title_user=message_title, checkin_id=0,status="unread",user_status="")
                                print("created4")

                                send_notification(receiver_obj, notification_id, notification_type,
                                                  message, message_title, sender_profile, sender_id, str(obj_id))
                            except:
                                pass


            else:
                message = "You are already checked in at {beershop}. Do you want to check out?".format(beershop = beercheckin_obj[0].beer.name)
                return_data ={
                    "beer_id":beercheckin_obj[0].beer.id,
                    "beer_name":beercheckin_obj[0].beer.name
                }
                return success_response(message, return_data)

            if 'check_in_status'in data:
                beercheck_obj.message = data["check_in_status"]
                beercheck_obj.save()
        message = "success"
        return success_response(message, return_data)

# ==================================================================================================
class CheckInLikeAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args,**kwargs):
        try:
            data = request.data
        
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            print(platform, device_id, app_version)

            return_data ={}
            user_obj = request.user

            sender_obj= user_obj
            sender_id= user_obj.id
            sender_profile = request.build_absolute_uri(user_obj.profile_img.url) if user_obj.profile_img else ""

            obj_id = data["id"]
            receiver = data["user_id"]
            receiver_obj=User.objects.get(id=receiver)
            # print(type(receiver_obj))

            try:
                event_obj = Event.objects.get(id=obj_id,created_by = receiver_obj) # is_active=True
            except ObjectDoesNotExist:
                return_data={"status" : 0,"message" : "Event is already finished.","data" : {}}
                return error_response("error",return_data)
            
            beercheckin_obj = BeerCheckIn.objects.filter(user=receiver_obj,beer=event_obj.beer_shop) #,status=True)
            print("checkin id",beercheckin_obj)
            if beercheckin_obj is None:
                return_data={"status" : 0,"message" : "error","data" : {"data":"checkin is not active"}}
                return error_response("error",return_data)



            checkinid=beercheckin_obj[0].id
            print(checkinid)

            if beercheckin_obj.exists():
                message_obj = Message.objects.get(title="friend",type="other")
                message = message_obj.text_message.format(username=sender_obj.first_name,beershop=event_obj.beer_shop.name)
                message_title = message_obj.message_title
                notification_id = create_notification(sender_obj, receiver_obj, message,obj_id,checkin_id=checkinid,title_base="friend", type_base="other",title_user=message_title, status="unread",user_status="")
                print(notification_id)
                notification_type = 2
                send_notification(receiver_obj, notification_id, notification_type,
                                                          message, message_title, sender_profile, sender_id, str(obj_id))
                print("sent")

                notification_obj1=Notification.objects.get(id=data["notification_id"])
                # print("-------",notification_obj1.id)

                notification_obj1.like = data["like"]
                notification_obj1.checkin_id = checkinid
                notification_obj1.like_notification_id=notification_id
                notification_obj1.save()

                return_data={"status" : 1,"message" : "success","data" : {}}
                return success_response("success",return_data)
        except Exception as e:
            return_data={"status" : 0,"message" : "error","data" : {"data":e}}
            return error_response("error",return_data)

        

    def put(self, request, *args,**kwargs):
        try:
            data = request.data
            print(data,request.user)
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            print(platform, device_id, app_version)

            return_data = {}
            user_obj = request.user
            user = User.objects.get(id=user_obj.id)
            print(user)
            notification_obj=Notification.objects.get(id=data["notification_id"])
            like_noti = notification_obj.like_notification_id
            print(notification_obj,like_noti)

            notification_obj.like = data["like"]
            

            like_notification_obj=Notification.objects.get(id=like_noti)
            print(like_notification_obj)
            like_notification_obj.delete()

            notification_obj.like_notification_id = 0
            notification_obj.save()

            return_data={"status" : 1,"message" : "success","data" : {}}
            return success_response("Dislike success full",return_data)

        except Exception as e:
            return_data={"status" : 0,"message" : "error","data" : {"data":e}}
            return success_response("Dislike error",return_data)


# ==================================================================================================


class BeerCheckOutAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args,**kwargs):
        data = request.data
        print("checkout",data)
        serializer = BeerCheckOutSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            beer_id = data["beer_id"]
            user_obj = request.user
            try:
                beerdetail_obj = BeerDetail.objects.get(id=beer_id)
            except:
                message = "Beer Detail is not available with us."
                return error_response(message, return_data)
            beercheck_obj = BeerCheckIn.objects.filter(user=user_obj, beer=beerdetail_obj, status = True)
            if not beercheck_obj.exists():
                message = "User is already checked out."
                return error_response(message, return_data)
            event_obj = Event.objects.filter(created_by = user_obj,beer_shop = beerdetail_obj,is_active = True)
            if event_obj.exists():
                beercheckedin_obj = BeerCheckIn.objects.filter(
                    beer=beerdetail_obj, event=event_obj[0], status=True).exclude(user=user_obj)
                if not beercheckedin_obj.exists():
                    event_obj.update(is_active = False)


            if 'check_out_status' in data:
                beercheck_obj.message = data["check_out_status"]

            if 'images' in data:
                print(data['images'],"imaaaaages")
                for image in data.getlist('images'):
                    check_out_image_obj, created = CheckOutImage.objects.get_or_create(checkout_image = image)
                    beercheck_obj.images.add(check_out_image_obj.id)
            imagelist = []
            beercheck_image_obj = beercheck_obj[0].images.all()
            imagecheckout = CheckoutImageSerializer(beercheck_image_obj, many=True, context={'request': request})
            for image in imagecheckout.data:
                imagelist.append(image['image'])
            return_data["image"] = imagelist

            if beercheck_obj.exists():
                beercheck_obj.update(status=False)

            message = "success"
            return success_response(message, return_data)



class UserFavouriteAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)

        validate_headers(platform, device_id, app_version)
        user_obj = request.user
        favourite_obj = UserFavourite.objects.filter(user=user_obj, status=True).order_by("-updated_at")
        serializer = GetUserFavouriteSerializer(favourite_obj, context={'request': request},many=True)
        return_data = serializer.data
        message = "success"
        return success_response(message, return_data)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserFavouriteSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            user_obj = request.user
            beer_id = data['beer_id']
            status = data['status']

            try:
                beerdetail_obj = BeerDetail.objects.get(id=beer_id)
            except:
                message = "Beer Detail is not available with us."
                return error_response(message, return_data)

            userfavourite_obj = UserFavourite.objects.filter(beer_shop = beerdetail_obj,user = user_obj)
            if userfavourite_obj.exists():
                userfavourite_obj.update(status = status)
            else:
                userfavourite_obj = UserFavourite.objects.create(beer_shop = beerdetail_obj,user = user_obj,status = status)
        message = "success"
        return success_response(message, return_data)


class RatingAPIView(APIView):
    permission_classes = [IsAllowed,]

    def get(self, request, *args, **kwargs):
        data = request.GET
        serializer = GetBeerDetailSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            return_data ={}
            validate_headers(platform, device_id, app_version)
            id = data["id"]

            try:
                beerdetail_obj = BeerDetail.objects.get(id=id)
            except:
                message = "Beer Detail is not available with us."
                data = {}
                return error_response(message, data)

            ratings_obj = Rating.objects.filter(beer_shop = beerdetail_obj)
            ratings_obj = ratings_obj.order_by("-created_at")
            serializer = GetRatingSerializer(ratings_obj, context={'request': request},many = True)
            return_data = serializer.data
        message = "success"
        return success_response(message, return_data)

    def post(self, request, *args, **kwargs):
        data = request.data
        print("DATA::",data)
        serializer = RatingSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            return_data = {}
            user_id = request.user.id
            beer_id = data['beer_id']
            rating = data['rating']
            user_obj = request.user
            try:
                beerdetail_obj = BeerDetail.objects.get(id=beer_id)
            except:
                message = "Beer Detail is not available with us."
                return error_response(message, return_data)
            rating_obj = Rating.objects.create(beer_shop = beerdetail_obj,user = user_obj,rating = rating)
            if 'feedback' in data:
                rating_obj.feedback = data['feedback']
            rating_obj.save()
            message = "success"
            return success_response(message, return_data)


class LocationWiseBeerAPIView(APIView):
    permission_classes = [IsAllowed,]

    def post(self, request, *args,**kwargs):
        data = request.data
        # serializer = BeerCheckOutSerializer(data=data)
        if data:
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            hit_google_api = True
            beer_category = data["category"]
            lat1 = float(data['latitude'])
            lon1 = float(data['longitude'])
            user_obj = request.user
            beerplaces_obj = BeerPlacesDetail.objects.filter(category=beer_category)
            print(len(beerplaces_obj))
            if beerplaces_obj:
                try:
                    radius = float(ConfigParam.objects.all()[0].config['search_radius'])
                except:
                    radius = 5.0
                min_distance = 0.0
                count = 0
                for beerplace in beerplaces_obj:
                    # call haversine formula
                    lat2, lon2 = float(beerplace.location['lat']), float(beerplace.location['lng'])
                    distance = haversine(lat1, lon1, lat2, lon2)
                    if distance < radius:
                        if count == 0:
                            min_distance = distance
                            return_data = beerplace.data
                            # print(return_data, 'first if')
                        if distance < min_distance:
                            min_distance = distance
                            return_data = beerplace.data
                            # print(return_data,'seconf if')
            else:
                pass
            # print("aaaaaa", return_data)
            if not return_data:
                hit_google_api = False
            
            message = "success"
            return success_response(message, return_data)


class BeerPlacesSaveAPIView(APIView):
    permission_classes = [IsAllowed,]

    def post(self, request, *args,**kwargs):
        data = request.data
        # serializer = BeerCheckOutSerializer(data=data)
        if data:
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            BeerPlacesDetail.objects.create(category=data['category'], location=data['location'], data=data['data'])
            message = "success"
            return success_response(message, return_data)

# ===================Nearby Offers and Checkins =======================
def findnearby(lat1,lon1):
    result=[]
    beerplaces_obj = BeerDetail.objects.all()
    if beerplaces_obj:
        try:
            radius = float(ConfigParam.objects.all()[1].config['search_radius'])
        except:
            radius = 5.0
        min_distance = 0.0
        count = 0
        for beerplace in beerplaces_obj:
            # call haversine formula
            if not beerplace.geometry:
                continue
            lat2, lon2 = float(beerplace.geometry["location"]["lat"]), float(beerplace.geometry["location"]["lng"])
            distance = haversine(lat1, lon1, lat2, lon2)
            if distance < radius:
                if count == 0:
                    min_distance = distance
                    result.append(beerplace.place_id) 

                if distance < min_distance:
                    min_distance = distance
                    result.append(beerplace.place_id) 
    return result

class NearbyOffers_FriendCheckinAPIView(APIView):
    permission_classes = [IsAllowed,]

    def post(self, request, *args,**kwargs):
        data = request.data
        user = request.user
        print(data, "DATA")
        print(user, "user")

        if data:
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)

        lat = float(data["latitude"])
        lon = float(data["longitude"])
        brewery = findnearby(lat, lon)
        print(brewery, "nearby brewery")

        friend_list = UserFriend.objects.filter(user=user, status="accepted")
        print(friend_list, "friendlist")

        admin_obj = User.objects.filter(groups__name='admin')
        sender_obj = admin_obj[0]
        sender_id = sender_obj.id
        sender_profile = request.build_absolute_uri(
                            admin_obj[0].profile_img.url) if admin_obj[0].profile_img else ""
        receiver_obj = user
        obj_id = 0
        try:
            for beer in brewery:
                print(beer,"beeeeeeeeeeeer")
                try:
                    obj = Brewery.objects.get(place_id=beer)
                    # print(obj, "Brewery=========")
                except Brewery.DoesNotExist:
                    continue
                beer_offer = Offer.objects.filter(user_id=obj, expired=False, live=True)
                print(beer_offer, "Offers=======")
                beer_data = BeerDetail.objects.get(place_id=beer)

                print("beer_data=>",beer_data)
                if beer_offer and beer_data:
                    # beer_data = BeerDetail.objects.get(place_id=beer)
                    object_ = get_beer_detail(beer_data)
                    object_["id"] = str(object_["id"])
                    object_["types"] = []

                    beer_obj = json.dumps(object_)

                    message_obj = Message.objects.get(title="offers",type="other")
                    message = message_obj.text_message.format(beershop=beer_data.name)
                    message_title = message_obj.message_title
                    notification_id = create_notification(sender_obj, receiver_obj, message,obj_id,checkin_id=0,title_base="offers", type_base="other",title_user=message_title, status="unread",user_status="")
                    notification_type = 5
                    send_notification(receiver_obj, notification_id, notification_type,
                                                            message, message_title, beer_obj, sender_id, str(obj_id)) # senderprofile replce withbeer_obj

                for friend_obj in friend_list:
                    friend = User.objects.get(id=friend_obj.friend.id)
            
                    try:
                        event = Event.objects.filter(name=beer_data.name, created_by=friend, beer_shop=beer_data, is_active=True) 
                        for event_obj in event:
                            beercheckin_obj = BeerCheckIn.objects.get(beer=beer_data, user=friend, event=event_obj, status=True)
                            obj_id = event_obj.id #event id

                            message_obj = Message.objects.get(title="checkin", type="other")
                            message = message_obj.text_message.format(username=friend.first_name,
                                                                                beershop=beer_data.name)
                            message_title = message_obj.message_title
                            notification_type = 2  ### checkin type ####
                            
                            notification_id = create_notification(sender_obj, receiver_obj, message,obj_id,
                                                                title_base="checkin", type_base="other",
                                                                title_user=message_title, checkin_id=beercheckin_obj.id,status="unread",user_status="")
                    
                            send_notification(receiver_obj, notification_id, notification_type,
                                                message, message_title, sender_profile, sender_id, str(obj_id))
                    except Event.DoesNotExist as e: 
                        continue
                    except BeerCheckIn.DoesNotExist as f:
                        continue
                    except Exception as e:
                        print(str(e))
                        message = "error"
                        return error_response(message, {"error" : str(e)})
        except Exception as e:
            print(str(e))
            return error_response(message, {"error" : str(e)})

                

            

        return_data = {"status" : 1,"message" : "success","data" : {}}
        message = "success"
        return success_response(message, return_data)

