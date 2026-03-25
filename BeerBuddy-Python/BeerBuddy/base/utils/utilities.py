import string
from collections import OrderedDict
from random import choice
from random import randint
from users.models import *
from beershop.models import *
from event.models import *
from notification.models import *
from brewery.models import *
from base.communications.sms_sender import SMSSender
from decouple import config
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email
from django.utils.crypto import get_random_string
# from .sms_sender import SMSSender, settings
from rest_framework import exceptions
from rest_framework import status
from rest_framework.response import Response
from base.communications.apn_sender import APNSender
from base.communications.fcm_sender import FCMSender
from django.db.models import Avg
import math
from pyfcm import FCMNotification
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

def notification_log(response, device_name):
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    final_data = dt_string + "\t\t" + device_name+ "==>" + str(response)

    date = now.strftime('%m-%d-%Y')
    file_object = open('../Firebase/notification_log('+date+').txt', 'a')
    file_object.write(final_data+"\n\n")
    file_object.close()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh),
           'access': str(refresh.access_token),}
           
def generate_passcode():
    """
    Method for generate random 4 digits passcode
    """

    return randint(1000, 9999)


def send_verification_sms(mobile, passcode):
    """
    Method for sending Clx mblox message
    """
    if config('CLX_MBLOX_TEST_MODE', default=False, cast=bool):
        mobile = config('CLX_MBLOX_TEST_NUMBER')

    sms = SMSSender(mobile,
                    "Enter {0} on the sign up page to verify your account. This is one time message.".format(passcode))

    sms.send()


def send_verification_email(email, passcode):
    subject = 'Verify your email address.'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]
    message = "Your verification code for Beer Buddy is {0}".format(passcode)
    try:
        send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=True,
        )
        # msg = EmailMultiAlternatives(subject, message, from_email, to_email)
        # msg.send()
    except Exception as e:
        print(str(e))

    return None


def generate_username(country_code, mobile_number):
    """
    Method for generate username
    """

    return "{0}{1}".format(country_code, mobile_number)


def is_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_reset_password_message(mobile, passcode):
    """
    Method for sending twilio message
    """
    if config('CLX_MBLOX_TEST_MODE', default=False, cast=bool):
        mobile = config('CLX_MBLOX_TEST_NUMBER')

    sms = SMSSender(mobile,
                    " Your verification code for Beer Buddy is {0}.".format(
                        passcode))

    sms.send()


def send_reset_password_email(email, passcode):
    subject = 'Recovery code for reset password'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]
    message = "Enter {0} on the Forgot password page to recovery your password . This is one time message.".format(
        passcode)

    send_mail(
        subject,
        message,
        from_email,
        to_email,
        fail_silently=True,
    )

    return None


def generate_random_string(length):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    random_string = get_random_string(length, chars)

    return random_string


def random_string_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(choice(chars) for _ in range(size))


def unique_username_generator(instance):
    username_new_id = random_string_generator()

    Klass = instance.__class__

    qs_exists = Klass.objects.filter(username=username_new_id).exists()
    if qs_exists:
        return unique_username_generator(instance)
    return username_new_id


def validate_headers(platform, device_id, app_version):
    if not platform:
        raise exceptions.ValidationError(detail="The platform field is required.")

    if not device_id:
        raise exceptions.ValidationError(detail="The device_id field is required.")

    if not app_version:
        raise exceptions.ValidationError(detail="The app_version field is required.")


def error_response(message, data={}):
    item_dict = OrderedDict()
    item_dict['status'] = 3
    item_dict['message'] = message
    item_dict['data'] = data
    return Response(item_dict, status=status.HTTP_400_BAD_REQUEST)


def success_response(message, data):
    item_dict = OrderedDict()
    item_dict['status'] = 1
    item_dict['message'] = message
    item_dict['data'] = data
    return Response(item_dict, status=status.HTTP_200_OK)

def generate_contact(country_code, mobile_number):
    """
    Method for generate username
    """

    return "{0}-{1}".format(country_code, mobile_number)


def get_favourite(user_obj,beer_shop_obj):
    favourite = UserFavourite.objects.filter(user=user_obj, beer_shop=beer_shop_obj)
    favourite = favourite[0].status if favourite.exists() else False
    return favourite

def deEmojify(inputString):
    return inputString.encode('ascii','ignore').decode('ascii')

def save_beer_detail_json(item):
    try:
        geometry = item['geometry']
        icon = item['icon']
        id = item['id']
        name = deEmojify(item['name'])
        place_id = item['place_id']
        plus_code = item['plus_code']
        photos = item['photos']
        reference = item['reference']
        scope = item['scope']
        vicinity = item['vicinity']
        formatted_address = item['formatted_address']
        types = len(item['types'])
        google_id = id
        brewery_id = item['brewery_id']
        print(brewery_id, "brewery")
        if brewery_id != 0:
            print("hello")
            brewery = Brewery.objects.get(id=brewery_id)
            print(brewery, "offers brewery")
            beerdetail_obj, create = BeerDetail.objects.get_or_create(
            brewery = brewery)
            print(beerdetail_obj, "breweryside")
            beerdetail_obj.brewery_id = brewery_id
        else:
            beerdetail_obj, create = BeerDetail.objects.get_or_create(
            place_id = place_id)
            print(beerdetail_obj, "barside")

        beerdetail_obj.geometry = geometry
        beerdetail_obj.icon = icon
        beerdetail_obj.name = name

        beerdetail_obj.place_id = place_id
        beerdetail_obj.plus_code = plus_code
        beerdetail_obj.photos = photos
        beerdetail_obj.reference = reference
        beerdetail_obj.scope = scope
        beerdetail_obj.vicinity = vicinity
        beerdetail_obj.formatted_address = formatted_address
        print(beerdetail_obj, "BeerDetail")
        beerdetail_obj.save()
        for type in range(types):
            name = item['types'][type]
            beertype_obj, created = BeerType.objects.get_or_create(name=name)
            beerdetail_obj.types.add(beertype_obj.id)

        if brewery_id != 0:
            print(beerdetail_obj.brewery, "return")
            return beerdetail_obj.brewery
        else:
            return place_id
    except Exception as e:
        print("Error save beer detail", e)
        return None

def get_avg_rating(beer_shop):
    rating_obj = Rating.objects.filter(beer_shop = beer_shop)
    rating = rating_obj.aggregate(Avg('rating'))['rating__avg'] if rating_obj.exists() else 0
    return rating

def get_total_users_check_in(beer_shop,user_id):
    total_users_check_in = BeerCheckIn.objects.filter(beer=beer_shop, status=True).exclude(user = user_id).count()
    return total_users_check_in

def get_user_check_in(user_obj,beer_shop_obj):
    users_checkin = BeerCheckIn.objects.filter(user=user_obj, beer=beer_shop_obj, status=True).order_by("-updated_at")
    if users_checkin.exists():
        return True
    else:
        return False

def social_phone_update_message(mobile, passcode):
    """
    Method for sending twilio message
    """
    if config('CLX_MBLOX_TEST_MODE', default=False, cast=bool):
        mobile = config('CLX_MBLOX_TEST_NUMBER')

    sms = SMSSender(mobile,"Enter {0} on the Mobile Update . This is one time message.".format(passcode))
    sms.send()

def get_beer_detail(beer_shop):
    types =[]
    beer_shop_name={}
    for type in beer_shop.types.all():
        beer_shop_name ={"name":type.name}
        types.append(beer_shop_name)
    beer_shop1 = {
        "id" : beer_shop.id,
        "geometry" : beer_shop.geometry,
        "icon" : beer_shop.icon,
        "google_id" : beer_shop.google_id,
        "name" : beer_shop.name,
        "place_id" : beer_shop.place_id,
        "plus_code" : beer_shop.plus_code,
        "photos" : beer_shop.photos,
        "reference" : beer_shop.reference,
        "scope" : beer_shop.scope,
        "types" : types,
        "vicinity" : beer_shop.vicinity,
        "formatted_address" : beer_shop.formatted_address if beer_shop.formatted_address else "",
    }
    return beer_shop1

def get_checkout_img(request,beer_shop):
    checkout_image = []
    checkout_images = BeerCheckIn.objects.filter(beer=beer_shop)
    for images in checkout_images:
        for image in images.images.all():
            checkout_image.append(request.build_absolute_uri(image.checkout_image.url))
    checkout_images_count = len(checkout_image)
    checkout_image.insert(0, checkout_images_count)
    return checkout_image

def create_notification(sender_obj,receiver_obj,message,obj_id,title_base,type_base,title_user,checkin_id,status="unread",user_status=""):

    try:
        print("tryyyyyyy")
        notification_obj = Notification.objects.create(
            user=receiver_obj,
            sender_id=sender_obj,
            obj_id=obj_id,
            message=message,
            type_base = type_base,
            title_base = title_base,
            title_user = title_user,
            status = status,
            user_status = user_status,
            checkin_id=checkin_id)
    except Exception as e:
        print(e)
    return notification_obj.id


def send_notification(receiver_obj,notification_id,notification_type,message,message_title,sender_profile,sender_id,obj_id=""):
    print("hello")
    file_object = open('Firebase_log.txt', 'a')
    user_devices = receiver_obj.devicedetail_set.all()
    print(user_devices)
    try:
        for device in user_devices:
            badge_counts = Notification.objects.filter(user = device.user,status = "unread").count()
            if badge_counts > 99:
                badge_count = 99
            else:
                badge_count = badge_counts
            friends_badges = UserFriend.objects.filter(friend = device.user,status = "pending",read_status = False).count()
            if friends_badges > 99:
                friends_badge = 99
            else:
                friends_badge = friends_badges

            if not device.device_token:
                continue
            if device.is_ios():
                message_title=message_title
                message_body=message
                data_message = {"badge":badge_count,
                          "title": message_title,"user_id":sender_id,
                          "user_profile":sender_profile,"id":obj_id, 
                          "notification_id":notification_id,
                          "notification_type":notification_type,"message": message,
                          "friends_badge":friends_badge}
                
                push_service = FCMNotification(api_key="AAAAaSAi3us:APA91bFcN25-wIQuQKQfaRnxtVU8y6Ja-FYiW6Y0PeA7sP7xA7UTjQ--iEsctx7cvTgo65QkDFKhbOrn2HAG1b6KSWV3__uuWBlHhm4bppsIJmfF_kBgrmt_uG8gmtE_QxF2q5KgBVkh")

                response = push_service.notify_single_device(registration_id=device.device_token,
                                   message_title=message_title,
                                   message_body=message_body,
                                   data_message=data_message,
                                   badge=badge_count,
                                   sound="default",
                                   extra_kwargs={"apns_push_type": "alert"})
                                   
                print("ios==>",response)
                notification_log(response,"ios")
                return response

                # apn = APNSender( device.device_token, text={"title":message_title,"body":message},badge = badge_count,
                #     custom={"friends_badge":friends_badge,"data":{"title": message_title,"user_id":sender_id,"user_profile":sender_profile,"id":obj_id, "notification_id":notification_id,"notification_type":notification_type,"message": message}}

                #     )
                # apn.send()
             
            elif device.is_android():
                fcm = FCMSender(to=device.device_token,data={"title": message_title,"user_id":sender_id,
                                                                "user_profile":sender_profile,"id":obj_id,
                                                                "notification_id":notification_id,
                                                                "notification_type":notification_type,
                                                                "message": message})
                # print("ANDROID_FCM--->",fcm)
                fcm.send()
    except Exception as e:
        print("error",e)
        return e

def haversine(lat1, lon1, lat2, lon2):
    # distance between latitudes 
    # and longitudes 
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
  
    # convert to radians 
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
  
    # apply formulae 
    a = (pow(math.sin(dLat / 2), 2) + 
         pow(math.sin(dLon / 2), 2) * 
             math.cos(lat1) * math.cos(lat2)); 
    rad = 6371
    c = 2 * math.asin(math.sqrt(a)) 
    return rad * c 
  
    # # Driver code 
    # if __name__ == "__main__": 
    #     lat1 = 51.5007
    #     lon1 = 0.1246
    #     lat2 = 40.6892
    #     lon2 = 74.0445
    # print(haversine(lat1, lon1,lat2, lon2), "K.M.")
