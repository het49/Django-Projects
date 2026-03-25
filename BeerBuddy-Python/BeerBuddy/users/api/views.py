from base.utils.utilities import (generate_passcode, send_verification_sms, send_verification_email, send_reset_password_message,
                                  validate_headers, success_response, error_response, generate_contact,
                                  social_phone_update_message, send_notification, create_notification,
                                  send_reset_password_email, get_tokens_for_user)
from django.contrib.auth import authenticate
from notification.models import *
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import (
    AllowAny, )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from users.api.permissions import IsAllowed
from users.models import *
from users.tasks import checkin_user
from notification.models import *
from beershop.models import BeerDetail
from event.models import BeerCheckIn
from .serializers import *
from django.contrib.auth.models import Group
from django.db.models import Count, Q
from pyfcm import FCMNotification

from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()

class CountryAPIView(generics.ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]

    def list(self, request):
        try:
            queryset = self.get_queryset().filter(is_active = True)
        except:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR , "message": "Country list- Internal Server Error ", "data": {}})

        serializer = CountrySerializer(queryset, many=True,context={"request": request})
        return Response({"status": status.HTTP_200_OK, "message": "success", "data": serializer.data})


class UserCreateAPIView(APIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            user_type = request.META.get('HTTP_USER_TYPE',None)

            validate_headers(platform, device_id, app_version)
            return_data = {}

            login_type = data['login_type']
            country_code = data.get('country_code', None)
            phone_no = data.get('phone_no', None)
            password = data['password']
            email = data['email']

            dob = data['dob']
            try:
                grp = Group.objects.get(name=user_type)
            except:
                message = "Invalid User Type."
                return error_response(message, return_data)

            if country_code and phone_no:
                phone = generate_contact(country_code,phone_no)

            user_obj = User.objects.filter(Q(username=email)|Q(email=email))
            print(user_obj,"user_obj")

            if user_obj.exists():
                if user_obj[0].is_mobile_verified ==True:
                    message = "An account with this mobile number or email-id already exists."
                    return error_response(message, return_data )
                else:
                    user_obj.delete()

            try:
                user_obj = User.objects.create_user(
                    username=email, password=password, dob=dob, phone_no=phone_no, email=email)
            except Exception as e:
                print(e)
                message = "User is registered with us"
                return error_response(message, return_data)


            passcode = generate_passcode()
            user_otp = OTPVerification.objects.filter(user=user_obj)

            if user_otp.exists(): ### user_otp
                user_otp.delete()

            OTPVerification.objects.create(user=user_obj, otp=passcode, is_verified=False)

            try:
                # send_verification_sms(phone, passcode)
                send_verification_email(email, passcode)
            except:
                message = "Message sent failed."
                return error_response(message, return_data)
            user_obj.is_mobile_verified = False
            user_obj.source=login_type
            user_obj.groups.add(grp)
            obj = TokenObtainPairSerializer()
            token = obj.validate({"username": email, "password": password})
            device_detail, created = DeviceDetail.objects.get_or_create(device_id=device_id)
            device_detail.user = user_obj
            device_detail.platform = platform
            device_detail.app_version = app_version
            device_detail.device_token = device_token
            device_detail.access_token = token.get('access')
            device_detail.refresh_token = token.get('refresh')
            device_detail.save()
            #user.save()
            if not request.META.get('HTTP_DEVICE_TOKEN', None):
                user_obj.notification_alert = False
                message = "Signup success. Allowing access to your notification helps us provide a better notification service."
            else:
                message = "Signup success."
            user_obj.save()
            return success_response(message,return_data)



class UserVerifyPasscodeAPIView(APIView):
    serializer_class = UserVerifyPasscodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserVerifyPasscodeSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            validate_headers(platform, device_id, app_version)

            country_code = data.get('country_code')
            phone_no = data.get('phone_no')
            email = data.get('email')
            passcode = data['passcode']
            
            if country_code and phone_no:
                username = generate_contact(country_code, phone_no)
                contact_obj = ContactList.objects.filter(number=phone_no)
                if contact_obj.exists():
                    contact_obj.update(beer_buddy_user=True)
            elif email:
                username = email
            
            return_data = {}
            try:
                user_obj = User.objects.get(username=username)
                print(user_obj)
            except:
                message = "User is not registered with us."
                return error_response(message, return_data)
            try:
                otp_obj = OTPVerification.objects.get(user = user_obj,otp = passcode)
            except:
                message = "Passcode doesnot match"
                return error_response(message, return_data)

            contact_obj = ContactList.objects.filter(number = phone_no)
            if contact_obj.exists():
                contact_obj.update(beer_buddy_user = True)

            serializer = GetImageSerializer(user_obj, context={'request': request})
            device_detail = DeviceDetail.objects.get(device_id=device_id)
            access_token = device_detail.access_token
            refresh_token = device_detail.refresh_token
            otp_obj.is_verified = True
            user_obj.is_mobile_verified = True
            user_obj.save()
            otp_obj.save()

        message = "success"
        return_data  = {
                "user_id": user_obj.id,
                "username": user_obj.username,
                "profile_image": serializer.data['profile_img'],
                "access_token": access_token,
                "refresh_token": refresh_token
                }
        return success_response(message, return_data )



class UserLoginAPIView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        data = request.data
        print("login",data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            user_type = request.META.get('HTTP_USER_TYPE', None)

            validate_headers(platform,device_id,app_version)
            return_data = {}
            login_type = data['login_type']


            if(login_type == 'normal'):
                print("cvvv")
                country_code = data.get('country_code')
                phone_no = data.get('phone_no')
                email = data.get('email')
                password = data['password']

                if country_code and phone_no:
                    username = generate_contact(country_code, phone_no)
                else:
                    username = email

                try:
                    user_obj = User.objects.all()
                    for i in user_obj:
                        if i.type == "":
                            i.type = "NORMALUSER"
                            i.save()
                        print(i.type,"type")
                    user_obj = User.objects.filter(username=username).filter(type="NORMALUSER")
                    print(user_obj,"user_obj")

                except Exception as e:
                    print(e,"err")

                try:
                    grp = Group.objects.get(name=user_type)
                except:
                    message = "Invalid User Type."
                    return error_response(message, return_data)
                if not user_obj.exists():
                    message = "User is not registered with us."
                    return error_response(message, return_data )

                if user_obj[0].is_mobile_verified == False:
                    message = "Inactive user"
                    data = {}
                    return error_response(message, return_data )
                
                # user_obj = authenticate(username=username, password=password)
                user_obj = authenticate(request, email=username, password=password)
                print("user_obj",user_obj)

                if not user_obj:
                    message = "Invalid Credentials"
                    return error_response(message, return_data)

                serializer = GetImageSerializer(user_obj, context={'request': request})
                # obj = TokenObtainPairSerializer()
                try:
                    token = get_tokens_for_user(user_obj)
                except Exception as e:
                    print(e)
            elif(login_type == 'social'):
                username = data['username']
                name = data['name']
                password = username + "Pass**9203"
                try:
                    grp = Group.objects.get(name=user_type)
                except:
                    message = "Invalid User Type."
                    return error_response(message, return_data)
                try:
                    serializer = GetImageSerializer(user_obj, context={'request': request})
                    obj = TokenObtainPairSerializer()
                    token = obj.validate({"username": username, "password": password})
                except:
                    try:
                        user_obj = User.objects.create_user(username=username, password=password)
                        user_obj.facebook_id = username
                        user_obj.first_name = name
                        user_obj.source = login_type
                        user_obj.groups.add(grp)
                        user_obj.save()
                        serializer = GetImageSerializer(user_obj, context={'request': request})
                        obj = TokenObtainPairSerializer()
                        token = obj.validate({"username": username, "password": password})
                    except:
                        message = "User is already registered with us."
                        return error_response(message, return_data)
            else:
                message = "Login type is invalid"
                return error_response(message, return_data)


            profile_update = True if user_obj.first_name and user_obj.city and user_obj.state else False
            phone = True if user_obj.phone_no else False
            device_detail, created = DeviceDetail.objects.get_or_create(device_id=device_id)
            device_detail.user = user_obj
            device_detail.platform = platform
            device_detail.device_token = device_token
            device_detail.access_token = token.get('access')
            device_detail.refresh_token = token.get('refresh')
            device_detail.save()
            return_data ={ "user_id": user_obj.id,
                   "username": user_obj.username,
                   "name": user_obj.first_name,
                   "phone": phone,
                   "profile_update": profile_update,
                   "profile_image":serializer.data['profile_img'],
                   "access_token": token.get('access'),
                   "refresh_token": token.get('refresh')}
        message = "success"
        return success_response(message, return_data)




class UserLogoutAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)

        validate_headers(platform, device_id, app_version)
        user_obj = request.user
        return_data = {}
        checkin_obj = BeerCheckIn.objects.filter(user=user_obj, status = True)
        if checkin_obj.exists():
           checkin_obj.update(status = False)

        try:
            device_detail = DeviceDetail.objects.get(platform = platform, user = user_obj,device_id = device_id)
            device_detail.delete()

        except User.DoesNotExist:
            message = "Inactive user"
            return error_response(message, return_data )
        except DeviceDetail.DoesNotExist:
            message = "User not login with us."
            return error_response(message, return_data )


        msg = "Logout successfully."
        message = "success"
        return success_response(message, return_data)



class RequestForgotPasswordAPIView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = ForgotPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)

            validate_headers(platform, device_id, app_version)

            country_code = data.get('country_code')
            phone_no = data.get('phone_no')
            email = data.get('email')

            return_data = {}

            if country_code and phone_no:
                username = generate_contact(country_code,phone_no)
            elif email:
                username = email

            try:
                user_obj = User.objects.get(username=username, is_active=True)
            except:
                message = "User is not registered with us."
                return error_response(message, return_data)


            passcode = generate_passcode()
            otp = OTPVerification.objects.filter(user = user_obj)
            if otp.exists():
                otp.delete()
            OTPVerification_obj=OTPVerification.objects.create(user = user_obj, otp = passcode)
            try:
                if country_code and phone_no:
                    send_reset_password_message(username, passcode)
                elif email:
                    send_reset_password_email(username, passcode)
            except:
                message = "Message sent failed."
                return error_response(message, return_data)
            OTPVerification_obj.is_verified = False
            OTPVerification_obj.save()

            message = "success"
        return success_response(message, return_data)


class VerifyForgetPasscodeAPIView(APIView):
    serializer_class = UserVerifyPasscodeSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserVerifyPasscodeSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)

            validate_headers(platform, device_id, app_version)

            country_code = data.get('country_code')
            phone_no = data.get('phone_no')
            email = data.get('email')
            passcode = data['passcode']

            if country_code and phone_no:
                username = generate_contact(country_code, phone_no)
            elif email:
                username = email

            return_data = {}
            try:
                user_obj = User.objects.get(username=username,type="NORMALUSER")
            except:
                message = "User is not registered with us."
                return error_response(message, return_data)
            try:
                otp_obj = OTPVerification.objects.get(user=user_obj, otp=passcode)
            except:
                message = "Passcode doesnot match"
                return error_response(message, return_data)

            otp_obj.is_verified = True
            otp_obj.save()
            message = "success"
            return success_response(message, return_data)


class VerifyForgotPasswordAPIView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = VerifyForgotPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)

            validate_headers(platform, device_id, app_version)

            return_data = {}
            
            country_code = data.get('country_code')
            phone_no = data.get('phone_no')
            email = data.get('email')

            if country_code and phone_no:
                username = generate_contact(country_code, phone_no)
            elif email:
                username = email

            new_password = data['new_password']
            try:
                user_obj = User.objects.get(username = username)
                user_obj.set_password(new_password)
                user_obj.save()
            except:
                message = "User doesnot exists."
                return error_response(message, return_data)

            serializer = GetImageSerializer(user_obj, context={'request': request})
            device_detail = DeviceDetail.objects.filter(user=user_obj)
            device_detail.delete()

            obj = TokenObtainPairSerializer()
            token = obj.validate({"username": username, "password": new_password})
            device_detail, created = DeviceDetail.objects.get_or_create(device_id=device_id)
            device_detail.user = user_obj
            device_detail.platform = platform
            device_detail.device_token = device_token
            device_detail.access_token = token.get('access')
            device_detail.refresh_token = token.get('refresh')
            device_detail.save()
            return_data = {"user_id": user_obj.id,
                           "username": user_obj.username,
                           "profile_image": serializer.data['profile_img'],
                           "access_token": token.get('access'),
                           "refresh_token": token.get('refresh')}
            message = "success"
            return success_response(message, return_data)

class ResetPasswordAPIView(APIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAllowed]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = ResetPasswordSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)

            validate_headers(platform, device_id, app_version)

            user_obj = request.user
            old_password = data['old_password']
            new_password = data['new_password']
            return_data = {}

            if user_obj.check_password(old_password):
                user_obj.set_password(new_password)
                user_obj.save()

                device_detail = DeviceDetail.objects.filter( user=user_obj)
                device_detail.delete()
            else:
                message = "Wrong password has been entered."
                return error_response(message, return_data)

            msg = "Password has been reset successfully. Please login again."
            message = "success"
            return success_response(message, return_data)



class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)

        validate_headers(platform, device_id, app_version)
        user_obj = request.user

        serializer = GetProfileSerializer(user_obj,context={'request': request})
        message = "success"
        return_data = serializer.data
        return success_response(message, return_data)


    def put(self,request,*args,**kwargs):
        data = request.data
        serializer = UpdateProfileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data ={}
            user_obj = request.user
            name = data['name']
            gender = data['gender']
            email = data['email']
            state = data['state']
            city = data['city']
            phone_no = data.get('phone_no', None)

            if 'date_of_birth' in data:
                date_of_birth = data['date_of_birth']
                try:
                    user_obj.dob = date_of_birth
                except:
                    message = "Date of birth has an invalid date format. It must be in YYYY-MM-DD format."
                    return error_response(message, return_data)

            user_obj.first_name = name
            user_obj.email = email
            user_obj.gender = gender
            user_obj.state = state
            user_obj.city = city
            if phone_no:
                user_obj.phone_no = phone_no
            if 'profile_img' in request.FILES:
                user_obj.profile_img =  request.FILES['profile_img']
            user_obj.save()
        serializer = GetProfileSerializer(user_obj, context={'request': request})
        message = "success"
        return_data = {
            "id":serializer.data['id'],
            "name":serializer.data['name'],
            "image_url":serializer.data['profile_img']
        }
        return success_response(message, return_data)




# class user contact list(APIView):
class UserContactListAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        validate_headers(platform, device_id, app_version)
        user_obj = request.user
        contacts_obj = ContactList.objects.filter(user = user_obj,beer_buddy_user = True).order_by('name')
        serializer = ContactListSerializer(contacts_obj,context={'request': request},many=True)
        return_data = serializer.data

        message = "success"
        return success_response(message, return_data)

    def post(self, request, *args, **kwargs):
        data = request.data
        if isinstance(data, dict):
            message = "No Contact match in beerbuddy"
            return_data = {}
            return error_response(message, return_data)
        serializer = AddContactListSerializer(data=data,many=True)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            user_obj = request.user
            if user_obj.contact.all():
                user_obj.contact.clear()
            for item in serializer.data:
                number = item['number']
                name = item['name']
                try:
                    user_available = User.objects.get(phone_no = number)
                    contactlist_obj, created = ContactList.objects.get_or_create(name = name,number = number)
                    contactlist_obj.beer_buddy_user = True
                    contactlist_obj.save()
                except:
                    contactlist_obj, created = ContactList.objects.get_or_create(name = name,number = number)
                user_obj.contact.add(contactlist_obj)
        message = "success"
        return_data = {}
        return success_response(message, return_data)



class GetAccessTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = RefreshTokenSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            refresh_token = data['refresh_token']

            try:
                device_detail = DeviceDetail.objects.get(refresh_token=refresh_token)
            except DeviceDetail.DoesNotExist:
                raise exceptions.NotFound(detail="Invalid Refresh Token")

            obj = TokenRefreshSerializer()
            token = obj.validate({"refresh": refresh_token})
            device_detail.access_token = token.get('access')
            device_detail.save()

            serializer = GetAccessTokenSerializer(device_detail)
            message = "success"
            return_data = serializer.data
            return success_response(message, return_data)


class UserFriendAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        validate_headers(platform, device_id, app_version)
        req_status = request.GET["status"]
        user_obj = request.user
        if req_status:
            friends_obj = UserFriend.objects.filter(status=req_status)

        else:
            friends_obj = UserFriend.objects.all()

        friend_list = []
        for friends in friends_obj:
            if friends.user == user_obj:
                serializer = GetUserFriendSerializer(friends,context={'request': request})
                friend_list.append(serializer.data)
            elif friends.friend == user_obj:
                serializer = GetUserFriendsSerializer(friends,context={'request': request})
                friend_list.append(serializer.data)

        sorted_friend_list = sorted(friend_list, key=lambda k: k['friend_name'])
        message = "success"
        return success_response(message, sorted_friend_list)

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = UserFriendSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            return_data = {}
            phone_no = data['friend']
            status = data['status']
            user_obj = request.user
            if status == 'pending' or status == 'cancel':
                try:
                    friend_obj = User.objects.get(phone_no=phone_no)
                except Exception as e:
                    try:
                        friend_obj = User.objects.get(email=phone_no)
                    except:
                        message = "User does not exist."
                        return error_response(message, return_data)
                if not user_obj.id == friend_obj.id:
                    friend_exist_obj = UserFriend.objects.filter(Q(user =user_obj,friend = friend_obj)|Q(user =friend_obj,friend = user_obj)).exclude(Q(status="rejected")|Q(status="cancel"))
                    if not friend_exist_obj.exists():
                        userfriend_obj = UserFriend.objects.create(user=user_obj, friend=friend_obj,status=status)
                    else:
                        if status == "cancel":
                            notification_obj = Notification.objects.filter(sender_id=user_obj,obj_id=friend_exist_obj[0].id)
                            notification_obj.update(user_status=status, status="delete")
                            friend_exist_obj.update(status = status)
                        else:
                            message = "you have already sent a friend request."
                            return error_response(message, return_data)
                    try:
                        message_obj = Message.objects.get(title="friend", type=status)
                        message = message_obj.text_message.format(sender=user_obj.first_name)
                        receiver_obj = friend_obj
                        sender_id = user_obj.id
                        sender_obj = user_obj
                        sender_profile = request.build_absolute_uri(
                            user_obj.profile_img.url) if user_obj.profile_img else ""
                        obj_id = userfriend_obj.id if not friend_exist_obj.exists() else friend_exist_obj[0].id
                        friend_phone = friend_obj.phone_no if friend_obj.phone_no else friend_obj.email
                        message_title = message_obj.message_title
                        notification_type = 0  ### friend ####
                        notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                                                              title_base="friend", type_base=status,
                                                              title_user=message_title, checkin_id=0,status="unread",
                                                              user_status=status)
                        send_notification(receiver_obj, notification_id, notification_type, message,
                                          message_title, sender_profile, sender_id, friend_phone)
                    except Exception as e:
                        print(e)
            else:
                message = "Status is invalid"
                return error_response(message,return_data)
            message = "success"
            return success_response(message, return_data)

    def put(self,request,*args,**kwargs):
        data = request.data
        serializer = UserFriendSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            return_data = {}
            phone_no = data['friend']
            status = data['status']
            user_obj = request.user
            if status == "accepted" or status == "rejected":
                try:
                    friend_obj = User.objects.get(phone_no=phone_no)
                except:
                    try:
                        friend_obj = User.objects.get(email=phone_no)
                    except:
                        message = "User does not exist."
                        return error_response(message, return_data)
                if not user_obj.id == friend_obj.id:
                    friend_exist_obj = UserFriend.objects.filter(user =friend_obj,friend = user_obj,status = "pending")

                    if friend_exist_obj.exists():
                        notification_obj = Notification.objects.filter(sender_id=friend_obj, obj_id=friend_exist_obj[0].id)
                        if status == "rejected":
                            notification_obj.update(user_status=status,status="delete")
                        else:
                            notification_obj.update(user_status=status)

                        try:
                            message_obj = Message.objects.get(title="friend", type=status)
                            message = message_obj.text_message.format(sender=friend_exist_obj[0].friend.first_name)
                            receiver_obj = friend_exist_obj[0].user
                            sender_id = friend_exist_obj[0].friend.id
                            sender_obj = friend_exist_obj[0].friend
                            sender_profile = request.build_absolute_uri(friend_exist_obj[0].friend.profile_img.url) if friend_exist_obj[0].friend.profile_img else ""
                            obj_id = friend_exist_obj[0].id
                            message_title = message_obj.message_title
                            notification_type = 3  ### friend ####
                            notification_id = create_notification(sender_obj,receiver_obj,message,obj_id,title_base ="friend",type_base = status,
                                                                  title_user = message_title,checkin_id=0,status = "unread",user_status = status)
                            friend_phone = friend_exist_obj[0].friend.phone_no if friend_exist_obj[0].friend.phone_no else friend_exist_obj[0].friend.email
                            if status == "accepted":
                                send_notification(receiver_obj, notification_id, notification_type, message,
                                                  message_title, sender_profile, sender_id, friend_phone)
                        except:
                            pass
                        friend_exist_obj.update(status=status,read_status=True)

                    else:
                        message = "You donot receive any friend request from {fullname}".format(fullname =friend_obj.first_name)
                        return error_response(message, return_data)
            else:
                message = "Status is invalid"
                return error_response(message, return_data)
            message = "success"
            return success_response(message, return_data)



class SocialPhoneUpdateAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = SocialPhoneUpdateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            country_code = data['country_code']
            phone_no = data['phone_no']
            phone = country_code +"-"+ phone_no

            user_obj = User.objects.filter(phone_no = phone_no)
            if user_obj.exists():
                message = "Mobile No. already exist"
                return error_response(message,return_data)
            else:
                user_obj = request.user
                passcode = generate_passcode()
                otp = OTPVerification.objects.filter(user=user_obj)
            if otp.exists():
                otp.delete()
            OTPVerification_obj = OTPVerification.objects.create(user=user_obj, otp=passcode)
            try:
                social_phone_update_message(phone, passcode)
            except:
                message = "Message sent failed."
                return error_response(message, return_data)
            OTPVerification_obj.is_verified = False
            OTPVerification_obj.save()

            message = "success"
        return success_response(message, return_data)


class SocialVerifyPasscodeAPIView(APIView):
    serializer_class = SocialVerifyPasscodeSerializer
    permission_classes = [IsAllowed]

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = SocialVerifyPasscodeSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            validate_headers(platform, device_id, app_version)

            country_code = data['country_code']
            phone_no = data['phone_no']
            passcode = data['passcode']
            return_data = {}
            user_obj = request.user
            try:
                otp_obj = OTPVerification.objects.get(user = user_obj,otp = passcode)
            except:
                message = "Passcode doesnot match"
                return error_response(message, return_data)


            contact_obj = ContactList.objects.filter(number = phone_no)
            if contact_obj.exists():
                contact_obj.update(beer_buddy_user = True)

            user_obj.phone_no = phone_no
            serializer = GetImageSerializer(user_obj, context={'request': request})
            device_detail = DeviceDetail.objects.get(device_id=device_id)
            access_token = device_detail.access_token
            refresh_token = device_detail.refresh_token
            otp_obj.is_verified = True
            user_obj.is_mobile_verified = True
            try:
                user_obj.save()
            except:
                message = "Mobile already exists()  "
                return error_response(message, return_data)

            otp_obj.save()
            phone = True if user_obj.phone_no else False


            message = "success"
            return_data = {"user_id": user_obj.id,
                "username": user_obj.username,
                "phone":phone,
                "profile_image": serializer.data['profile_img'],
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        return success_response(message, return_data )


class FriendSearchAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        data = request.GET
        return_data = []
        platform = request.META.get('HTTP_PLATFORM', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        user_type = request.META.get("HTTP_USER_TYPE")
        validate_headers(platform, device_id, app_version)
        search = data["search"]
        grp = Group.objects.get(name=user_type)
        friend_list = []
        user_list_obj = User.objects.filter(groups__id=grp.id).exclude(id=request.user.id)

        if search:
            if user_list_obj.exists():
                first_name_list = user_list_obj.filter(first_name__istartswith=search)
                list_of_id = list(first_name_list.values_list('id', flat=True))
                city_list = user_list_obj.filter(city__istartswith=search).exclude(id__in=list_of_id)
                list_of_id.extend(list((city_list.values_list('id', flat=True))))
                state_list = user_list_obj.filter(state__istartswith=search).exclude(id__in=list_of_id)
                list_of_id.extend(list((state_list.values_list('id', flat=True))))
                phone_no_list = user_list_obj.filter(phone_no__istartswith=search).exclude(id__in=list_of_id)
                list_of_id.extend(list((phone_no_list.values_list('id', flat=True))))
                user_serialized_list = SearchSerializer(first_name_list, context={'request': request}, many=True).data
                user_serialized_list.extend(SearchSerializer(city_list, context={'request': request}, many=True).data)
                user_serialized_list.extend(SearchSerializer(state_list, context={'request': request}, many=True).data)
                user_serialized_list.extend(SearchSerializer(phone_no_list, context={'request': request}, many=True).data)
                for user_id in user_serialized_list:
                    if friend_list:
                        if not any(friend["id"] == user_id["id"] for friend in friend_list):
                            # if user_id["phone"] is not "":
                            friend_list.append(user_id)
                            # else:
                            #     pass
                    else:
                        # if user_id["phone"] is not "":
                        friend_list.append(user_id)
                        # else:
                        #     pass
            else:
                message = "No records found"
                return success_response(message, return_data)
            if friend_list:
                # friend_list.sort(key=lambda k: k['name'])
                return_data = friend_list
                message = "success"
                return success_response(message, return_data)
            else:
                message = "No records found"
                return success_response(message, return_data)
        else:
            message = "Please provide valid input"
            return error_response(message, return_data)


class UserSetting(APIView):
    permission_classes = [IsAllowed]

    def put(self,request,*args,**kwargs):
        data = request.data
        serializer = SettingSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            return_data = {}
            setting_key = data['setting_key']
            user_obj = request.user
            if setting_key == "dob":
                if user_obj.dob_visible == True:
                    user_obj.dob_visible = False
                else:
                    user_obj.dob_visible = True
            elif setting_key == "contact":
                if user_obj.contact_visible == True:
                    user_obj.contact_visible = False
                else:
                    user_obj.contact_visible = True
            elif setting_key == "email":
                if user_obj.email_visible == True:
                    user_obj.email_visible = False
                else:
                    user_obj.email_visible = True
            user_obj.save()
            message = "success"
            return success_response(message, return_data)


class OtherUserProfile(APIView):
    permission_classes = [IsAllowed]

    def get(self,request,pk,*args,**kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        validate_headers(platform, device_id, app_version)
        return_data = {}
        try:
            user_obj = User.objects.get(id = pk)
        except:
            message = "User does not exist."
            return error_response(message, return_data)

        serializer = GetOtherProfileSerializer(user_obj, context={'request': request})
        message = "success"
        return_data = serializer.data
        return success_response(message, return_data)


class ResentOTP(APIView):
    permission_classes = [AllowAny]

    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = ResentOTPSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            validate_headers(platform, device_id, app_version)
            return_data = {}
            country_code = data.get('country_code')
            phone_no = data.get('phone_no')
            email = data.get('email')

            if country_code and phone_no:
                phone = generate_contact(country_code, phone_no)
                username = phone
                send_reset_password_info = send_reset_password_message
                send_verification_info = send_verification_sms
            elif email:
                username = email
                send_reset_password_info = send_reset_password_email
                send_verification_info = send_verification_email

            requested_type = data['requested_type']
            passcode = generate_passcode()
            if requested_type == "resend_create_otp" or requested_type == "resend_forget_password":
                try:
                    user_obj = User.objects.get(username=username, is_active=True)
                except:
                    message = "User is not registered with us."
                    return error_response(message, return_data)
                try:
                    if requested_type == "resend_forget_password":
                        send_reset_password_info(username, passcode)
                    else:
                        send_verification_info(username, passcode)
                except:
                    message = "Message sent failed."
                    return error_response(message, return_data)

            elif requested_type == "resend_social_phone_update":
                username = data['username']
                try:
                    user_obj = User.objects.get(username = username, is_active = True)
                except:
                    message = "User is not registered with us."
                    return error_response(message, return_data)

                # otp = OTPVerification.objects.filter(user = user_obj)
                # if otp.exists():
                #     otp.delete()
                # OTPVerification_obj = OTPVerification.objects.create(user = user_obj, otp = passcode)
                try:
                    social_phone_update_message(phone, passcode)
                except:
                    message = "Message sent failed."
                    return error_response(message, return_data)

            otp = OTPVerification.objects.filter(user=user_obj)
            if otp.exists():
                otp.delete()
            OTPVerification_obj = OTPVerification.objects.create(user=user_obj, otp=passcode)
            OTPVerification_obj.is_verified = False
            OTPVerification_obj.save()
            message = "success"
            return success_response(message, return_data)


class UserCheckedInBuddyAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args,**kwargs):
        data = request.data
        print("hi")
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)

        validate_headers(platform, device_id, app_version)
        user_obj = request.user
        
        return_data = {}
        user_buddies = UserFriend.objects.filter(Q(user=user_obj)|Q(friend=user_obj), status='Accepted')
        user_buddies_list = []
        for user_buddy_obj in user_buddies:
            if user_buddy_obj.user == user_obj:
                user_buddies_list.append(user_buddy_obj.friend)
            else:
                user_buddies_list.append(user_buddy_obj.user)
        if user_buddies_list:
            user_buddies_list = set(user_buddies_list)
        
        checked_in_buddies = BeerCheckIn.objects.filter(user__in=user_buddies_list, status=True)
        all_events = set(checked_in_buddies.values_list('beer__id', flat=True))
        data = []
        for element in all_events:
            element = BeerDetail.objects.get(id=element)
            response_dict = {'restaurant_name':element.name, 'restaurant_image':element.photos}
            buddies_list = []
            buddies = list(checked_in_buddies.filter(beer=element).values('user__id', 'user__first_name', 'user__last_name', 'user__profile_img'))
            for buddy in buddies:
                buddy_dict = {'user_name': buddy['user__first_name']+' '+buddy['user__last_name'], 'user_image': request.build_absolute_uri(
                    buddy['user__profile_img']).replace('api/users/checkedin_buddies', 'media'), 'user_id': buddy['user__id']}
                buddies_list.append(buddy_dict)
            response_dict['checked_in_buddies'] = buddies_list
            data.append(response_dict)
        return_data['checkin_data'] = data
        message = "success"
        return success_response(message, return_data)

# =======================================================================

class AppVersionAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)
        validate_headers(platform, device_id, app_version)
        return_data = {}
        app_version = []
        try:
            ios_version_obj = AppVersion.objects.filter(platform='ios')
            android_version_obj = AppVersion.objects.filter(platform='android')
            if ios_version_obj.exists():
                app_version.append(ios_version_obj[0])
            if android_version_obj.exists():
                app_version.append(android_version_obj[0])
        except:
            message = "App version data does not exist."
            return error_response(message, return_data)
        for item in app_version:
            serializer = AppVersionSerializer(
                item, context={'request': request})
            return_data[item.platform] = serializer.data
        message = "success"
        return success_response(message, return_data)

# =======================================================================


