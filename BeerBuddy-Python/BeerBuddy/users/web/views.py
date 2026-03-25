import csv
import requests
from datetime import datetime
from base.utils.utilities import (generate_contact, error_response)
from base.staticcontent.models import Static
from django.contrib.auth import authenticate
from django.contrib.auth import logout as site_logout, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from event.models import BeerCheckIn
from users.models import User, Country, ContactList, UserFriend
from brewery.models import *
from users.web.serializers import (GetUserFriendSerializer, GetUserFriendsSerializer, 
                                  UserDetailListSerializer, BreweryCreateSerializer)
from django.contrib.auth.models import Group
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

# create your views here

class DashBoard(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):

        user_obj = User.objects.all().exclude(is_superuser=True)
        categories = []
        user_series = []
        if request.GET:
            graph_type = request.GET['type']
            if graph_type == 'weekly':
                per_week_user = user_obj.all().extra(
                    select={'week': "EXTRACT(week FROM created_at)"}).values(
                    'week').annotate(count_items=Count('created_at'))

                for entry in per_week_user:
                    if entry['week'] not in categories:
                        categories.append(entry['week'])
                        user_series.append(entry['count_items'])
            elif graph_type == 'monthly':
                per_month_user = user_obj.all().extra(
                    select={'month': "EXTRACT(month FROM created_at)"}).values(
                    'month').annotate(count_items=Count('created_at'))

                for entry in per_month_user:
                    if entry['month'] == 1:
                        categories.append('January')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 2:
                        categories.append('February')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 3:
                        categories.append('March')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 4:
                        categories.append('April')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 5:
                        categories.append('May')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 6:
                        categories.append('June')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 7:
                        categories.append('July')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 8:
                        categories.append('August')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 9:
                        categories.append('September')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 10:
                        categories.append('October')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 11:
                        categories.append('November')
                        user_series.append(entry['count_items'])
                    elif entry['month'] == 12:
                        categories.append('December')
                        user_series.append(entry['count_items'])

            elif graph_type == 'yearly':
                per_year_user = user_obj.all().extra(select={'year': "EXTRACT(year FROM created_at)"}).values(
                    'year').annotate(count_items=Count('created_at'))
                for entry in per_year_user:
                    if entry['year'] not in categories:
                        categories.append(entry['year'])
                        user_series.append(entry['count_items'])
            else:
                per_week_user=''
                per_month_user=''
                per_month_user=''

        total_deactive_user = user_obj.filter(is_active=False)
        new_user = user_obj.filter(created_at__startswith=datetime.now().date()).count()

        total_user = user_obj.count()
        total_length = len(str(user_obj.count()))

        maximum_user = 10 ** (total_length)
        total_user_percentage = (total_length / maximum_user) * 100

        total_deactive_percentage = (len(str(total_deactive_user.count())) / maximum_user) * 100
        total_percentage_newuser = (len(str(new_user)) / maximum_user) * 100

        checkin_obj = BeerCheckIn.objects.all()
        total_checkin_user = checkin_obj.count()
        total_length = len(str(total_checkin_user))
        maximum_checkin_user = 10 ** total_length
        total_checkin_percentage = (total_checkin_user / maximum_checkin_user) * 100

        context = {
            # 'per_week_user':per_week_user,
            # 'per_month_user':per_month_user,
            'categories': categories,
            'user_series': user_series,
            'new_user': new_user,
            'total_user': total_user,
            'total_checkin_user': total_checkin_user,
            'total_deactive_percentage': total_deactive_percentage,
            'total_percentage_newuser': total_percentage_newuser,
            'total_user_percentage': total_user_percentage,
            'total_checkin_percentage': total_checkin_percentage,
            'total_deactive_user': total_deactive_user.count(),
            "nbar": "dashboard"
        }

        return render(request, "users/web/admin/templates/dashboard.html", context)


# =========================== App User================================================
class UserManagement(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        user_list = User.objects.all().exclude(is_superuser=True).order_by('-created_at')
        return render(request, "users/web/admin/templates/user_managment.html",
                      {'user_list': user_list, "nbar": "user_managment"})
# ===========================================================================


class UserDownloadCsvView(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Phone Number', 'Email ID','City','State'])

        users = User.objects.all().exclude(is_superuser=True).order_by('created_at').values_list('first_name', 'phone_no', 'email', 'city','state',)
        for user in users:
            writer.writerow(user)

        return response


class ChangePassword(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        login_user = User.objects.get(id=request.user.id)
        return render(request, "users/web/admin/templates/change_password.html",
                      {'login_user': login_user, "nbar": "change_password"})

    def post(self, request):
        login_user = User.objects.get(id=request.user.id)
        old_password = request.POST.get('oldpassword')
        new_password = request.POST.get('newpassword')
        try:
            user = User.objects.get(id=request.user.id)
            if user:
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    site_logout(request)
                    msg = " Your Password has been changed,Please Login Again"
                    return render(request, "users/web/admin/templates/change_password.html",
                                  {'msg': msg, 'login_user': login_user, 'status': 'success'})

                else:
                    msg = 'Please Enter Correct Old Password'
                    return render(request, "users/web/admin/templates/change_password.html",
                                  {'msg': msg, 'login_user': login_user, 'status': 'error'})

            else:
                msg = 'User Is Not Registered'
                return render(request, "users/web/admin/templates/change_password.html",
                              {'msg': msg, 'status': 'error'})

        except:
            msg = "Please Fill Valid Information"
            return render(request, "users/web/admin/templates/change_password.html", {'msg': msg, 'status': 'error'})


class LoginView(View):
    def get(self, request):
        try:
            msg = request.session["msg"]
            del request.session["msg"]
        except:
            msg = ''
        return render(request, 'users/web/admin/templates/login.html', {"msg": msg})

    def post(self, request):
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            group_name = user.groups.filter(name='admin')
        if user is not None and group_name.exists():
            login(request, user)
            if not data.get('options'):
                request.session.set_expiry(0)
            # return redirect('/web/users/dashboard?type=weekly')
            return redirect('/web/users/brewery_management/')
        else:
            msg = "Username or Password is wrong"
            request.session["msg"] = msg
            return redirect('/web/users/login/')


class ProfileView(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        login_user = User.objects.get(id=request.user.id)
        countries = Country.objects.all()
        return render(request, "users/web/admin/templates/profile.html",
                      {"login_user": login_user, 'countries': countries})

    def post(self, request):
        countries = Country.objects.all()
        login_user = User.objects.get(id=request.user.id)
        user_obj = User.objects.get(id=request.user.id)
        user_obj.username = request.POST.get("username", user_obj.username)
        user_obj.first_name = request.POST.get("first_name", user_obj.first_name)
        user_obj.last_name = request.POST.get("last_name", user_obj.last_name)
        user_obj.email = request.POST.get("email", user_obj.email)
        user_obj.phone_no = request.POST.get("phone_no", user_obj.phone_no)
        user_obj.alternate_no = request.POST.get("alternate_no", user_obj.alternate_no)
        user_obj.dob = request.POST.get("dob", user_obj.dob)
        user_obj.gender = request.POST.get("gender", user_obj.gender)
        user_obj.city = request.POST.get("city", user_obj.city)
        user_obj.state = request.POST.get("state", user_obj.state)
        user_obj.country = Country.objects.get(id=request.POST.get('country', user_obj.country))
        user_obj.profile_img = request.FILES.get("profile_img", user_obj.profile_img)
        try:
            user_obj.save()
            message = "Profile Updated Successfully"
            return render(request, "users/web/admin/templates/profile.html",
                          {'message': message, 'is_message': 1, "login_user": login_user, 'countries': countries})
        except:
            message = "Mobile number and Alternate number should be unique"
            return render(request, "users/web/admin/templates/profile.html",
                          {'message': message, 'is_message': 0, "login_user": login_user, 'countries': countries})

        return redirect("/web/users/profile/")


class ChangeUserStatus(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        user_id = request.POST.get('id', False)
        try:
            user_obj = User.objects.get(id=user_id)
        except:
            return JsonResponse({'result': 2})
        if user_obj:
            if user_obj.is_active:
                user_obj.is_active = 0
            else:
                user_obj.is_active = 1
            user_obj.save()
        return JsonResponse({'result': user_obj.is_active})


class GetUserDetails(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        user_id = request.POST.get('id')
        user_obj = User.objects.get(id=user_id)
        user_details = UserDetailListSerializer(user_obj)
        if user_details is not None:
            result = user_details.data
            status = 'success'
        else:
            result = ''
            status = 'error'

        return JsonResponse({'result': result, 'status': status})


class GetBeerUserConnection(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        userid = request.POST.get('id')
        user_obj = User.objects.get(id=userid)
        friends_obj = UserFriend.objects.filter(user=user_obj,status="accepted")
        friend_list = []
        for friends in friends_obj:
            if friends.user == user_obj:
                serializer = GetUserFriendSerializer(friends, context={'request': request})
                friend_list.append(serializer.data)
            elif friends.friend == user_obj:
                serializer = GetUserFriendsSerializer(friends, context={'request': request})
                friend_list.append(serializer.data)
        if friend_list:
            result = friend_list
            status = 'success'
        else:
            result = ''
            status = 'error'

        return JsonResponse({'result': result, 'status': status})


def logout(request):
    site_logout(request)
    return redirect('/web/users/login/')


class PrivacyPolicy(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        privacy_policy = Static.objects.get(id=2)
        return render(request, "users/web/admin/templates/privacy-policy.html", {"privacy_policy": privacy_policy})


class EditPrivacyPolicy(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request, pk):
        privacy_policy = Static.objects.get(id=pk)
        return render(request, "users/web/admin/templates/edit-privacy-policy.html", {"privacy_policy": privacy_policy})

    def post(self, request, pk):
        try:
            privacy_obj = Static.objects.get(id=pk)
        except:
            return redirect("/web/users/privacy-policy/")

        privacy_obj.title = request.POST.get("title", privacy_obj.title)
        privacy_obj.content = request.POST.get("content", privacy_obj.content)
        try:
            privacy_obj.save()
        except:
            message = "Title is already exists"
            return render(request, "users/web/admin/templates/edit-privacy-policy.html",
                          {'message': message, 'is_message': 0})

        return redirect("/web/users/privacy-policy/")


class TermsCondition(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        terms_condition_obj = Static.objects.get(id=1)
        return render(request, "users/web/admin/templates/terms-condition.html",
                      {"terms_condition_obj": terms_condition_obj})


class EditTermsCondition(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request, pk):
        terms_condition_obj = Static.objects.get(id=pk)
        return render(request, "users/web/admin/templates/edit-terms-condition.html",
                      {"terms_condition_obj": terms_condition_obj})

    def post(self, request, pk):
        try:
            terms_condition_obj = Static.objects.get(id=pk)
        except:
            return redirect("/web/users/terms-condition/")

        terms_condition_obj.title = request.POST.get("title", terms_condition_obj.title)
        terms_condition_obj.content = request.POST.get("content", terms_condition_obj.content)
        try:
            terms_condition_obj.save()
        except:
            message = "Title is already exists"
            return render(request, "users/web/admin/templates/edit-terms-condition.html",
                          {'message': message, 'is_message': 0})

        return redirect("/web/users/terms-condition/")


class PieChartView(View):
    def get(self, request):
        usercheckin = BeerCheckIn.objects.values('user__city').annotate(
            total=Count('user__city'))
        chart = {
            'chart': {'type': 'pie'},
            'title': {'text': 'Checkin User'},

            'credits': {
                'enabled': False
            },
            'series': [{
                'name': 'Beer CheckIn',
                'data': list(map(lambda row: {'name': row['user__city'], 'y': row['total']}, usercheckin))
            }]
        }
        return JsonResponse(chart)


class DeleteUserView(View):
    def get(self, request, pk):

        user_obj = Brewery.objects.get(id=pk)
        user_obj.delete()
        return redirect("/web/users/brewery_management/")
# ==============================================================================================
class BreweryManagement(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        user_list = Brewery.objects.all().exclude(is_superuser=True).order_by('-created_at')
        print(user_list)
        return render(request, "users/web/admin/templates/user_managment.html",
                      {'user_list': user_list, "nbar": "brewery_managment"})

class BreweryRegister(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        return render(request, "users/web/admin/templates/brewery_registration.html",{"nbar": "brewery_register"})

    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request,*args,**kwargs):
        data = request.POST
        serializer = BreweryCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            login_type = "email"
            group_type = "breweryowner"
            country_code = data.get('country_code', None)
            phone_no = data.get('phone_no', None)
            username = data.get('username', None)
            password = data['password']
            cpassword = data['cpassword']
            email = data['email']

            try:
                grp = Group.objects.get(name=group_type)
            except:
                message = "Invalid User Type."
                return render(request, "users/web/admin/templates/brewery_registration.html",{"message":message,"nbar": "brewery_register"})

            if country_code and phone_no:
                phone = generate_contact(country_code,phone_no)

            user_obj = Brewery.objects.filter(email=email)
            print(user_obj)
            if user_obj.exists():
                # if user_obj[0].email==email:
                if user_obj[0].type=="BREWERY":
                    message = "A Brewery with this email-id is already exists Please try with another email."
                    return render(request, "users/web/admin/templates/brewery_registration.html",{"message":message,"nbar": "brewery_register"})
                # else:
                #     user_obj.delete()

            try:
                if password == cpassword:
                    print("if part")
                    user_obj1 = Brewery.objects.create_user(email=email,password=password, brewery_phone=phone_no, type="BREWERY")
                    print("created")
                    print(user_obj1)
                    # link = "http://" + settings.ALLOWED_HOSTS[0] + "/web/brewery/login/"
                    message_text = "BeerBuddy : Successfull Registration \n\nYou have been successfully added as a Brewery in Beerbuddy, Please find your credentials below, You can change your password later\n\n" + "Email :  " + user_obj1.email + "\nPassword : " + password
                    send_mail('BeerBuddy',message_text,settings.EMAIL_HOST_USER,[user_obj1.email],fail_silently=False)
                    print("done")

                    user_obj1.is_mobile_verified = False
                    user_obj1.source=login_type
                    user_obj1.groups.add(grp)
                
                    message = "Successfull registration of Brewery."
                    user_obj1.save()
                    return render(request, "users/web/admin/templates/brewery_registration.html",{"message":message,"nbar": "brewery_register"})
                else:
                    # print("else part")
                    message = "Password and Confirm Password do not match"
                    return render(request, "users/web/admin/templates/brewery_registration.html",{"message":message,"nbar": "brewery_register"})
            except Exception as e:
                print("except",e)
                message = "User with this Email id is already is registered with us"
                return render(request, "users/web/admin/templates/brewery_registration.html",{"message":message,"nbar": "brewery_register"})

            