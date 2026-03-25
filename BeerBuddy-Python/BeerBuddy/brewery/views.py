from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth import login as brewery_login, logout as brewery_logout
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from users.web.serializers import BreweryProfileSerializer
from brewery.models import Brewery, Offer
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from collections import OrderedDict
from datetime import datetime




# Create your views here.
def csrf_failure(request, reason=""):
    context = {"message" : "Sorry, there's been a problem posting your form. Please reload this page and try again."}
    return render(request, "brewery/web/admin/templates/csrf_failed.html",context)

def dashboard(request):
	user = request.user
	print(user.id,"user id")
	try:
		offers = Offer.objects.filter(brewery_owner=user.id)
	except Exception as e:
		print(str(e))
	print("offers", offers)

	return render(request,"brewery/web/admin/templates/dashboard.html",{"page":"DASHBOARD","offers":offers})

def OfferStatus(request, offer_id):
	obj = Offer.objects.get(id=offer_id)

	if obj.live == True:
		obj.live = False
		obj.expired = True
	else:
		obj.live = True
		obj.expired = False
	obj.save()
	return redirect('/web/brewery/brewery_dashboard/')


class LoginView(View):
	def get(self, request):
		try:
			msg = request.session["msg"]
			del request.session["msg"]
		except Exception as e:
			msg = ''
		return render(request, 'brewery/web/admin/templates/login.html', {"msg": msg})

	def post(self, request):
		print("post")
		data = request.POST
		try:
			email = data.get('email')
			password = data.get('password')
			user = authenticate(request, email=email, password=password, type="BREWERY")
			print(user)
			if user is None:
				print("inside")
				return render(request, 'brewery/web/admin/templates/login.html', {"msg": "Wrong credentials, Please use correct one!!"})

		except Exception as e:
			print("authenticate" , e)
		if user:
			group_name = user.groups.filter(name='breweryowner')
		if user is not None and group_name.exists():
			brewery_login(request, user)
			if not data.get('options'):
				request.session.set_expiry(0)
			return redirect('/web/brewery/profile/')
		else:
			msg = "Email or Password is wrong"
			request.session["msg"] = msg
			return redirect('/web/brewery/login/')
			
class LogoutView(View):
	def get(self, request):
		brewery_logout(request)
		return redirect('/web/brewery/login/')

class BreweryProfileView(View):
	@method_decorator(login_required(login_url='/web/brewery/login/'))
	def get(self, request):
		login_user = Brewery.objects.filter(id=request.user.id)
		print(login_user)
		return render(request, "brewery/web/admin/templates/brewery_profile.html",{"login_user": login_user, "page":"PROFILE"})

	def post(self, request,*args,**kwargs):
		try:
			place = {}
			login_user = Brewery.objects.get(id=request.user.id)
			print(login_user, "=========>Brewery")
			user_obj = Brewery.objects.get(id=request.user.id)
			user_obj.brewery_name = request.POST.get("brewery_name", user_obj.brewery_name)
			user_obj.first_name = request.POST.get("first_name", user_obj.first_name)
			user_obj.last_name = request.POST.get("last_name", user_obj.last_name)
			user_obj.place_id = request.POST.get("placeid", user_obj.place_id)
			user_obj.address = request.POST.get("address", user_obj.address)
			user_obj.brewery_desc = request.POST.get("desc", user_obj.brewery_desc)
			user_obj.profile_img = request.FILES.get("profile_img", user_obj.profile_img)
			raw_placedata = json.loads(request.POST.get("placedata"))

			print(type(user_obj.brewery_name),user_obj.brewery_name)

			key = settings.GOOGLE_PLACE_DETAIL_API_KEY
			place1 = request.POST.get("placeid")

			url = 'https://maps.googleapis.com/maps/api/place/details/json?'
			params = {
				"place_id": str(place1),
				"key": str(key),
				"fields" : 'geometry'
			}
			response = requests.get(url, params)
			detail = json.loads(response.text)
		
			raw_placedata["id"] = ""
			raw_placedata["brewery_id"] = login_user.id
			raw_placedata["geometry"] = detail["result"]["geometry"]
			raw_placedata["permanently_closed"] = ""

			lat = detail["result"]["geometry"]["location"]["lat"]
			lng = detail["result"]["geometry"]["location"]["lng"]
			user_obj.langitude = lat
			user_obj.longitude = lng

			place["data"] = raw_placedata
			place["data"]["name"] = user_obj.brewery_name
			place["brewery_name"] = user_obj.brewery_name
			place["place_id"] = user_obj.place_id
			place["latitude"] = user_obj.langitude
			place["longitude"] = user_obj.longitude
			place["profile_img"]= ""
			place["address"]=user_obj.address

			user_obj.placedata = place

			user_obj.save()

			image = request.build_absolute_uri(user_obj.profile_img.url)
			print(image,"image file")
			
			place_detail = user_obj.placedata
			place_detail["profile_img"] = image

			user_obj.placedata = place_detail
			user_obj.save()
			
			return redirect('/web/brewery/profile/')
		except Exception as e:
			print(e)
			return render(request, "brewery/web/admin/templates/brewery_profile.html",{"message":e, "page":"PROFILE"})

class Change_Password(View):
    @method_decorator(login_required(login_url='/web/brewery/login/'))
    def get(self, request):
        login_user = Brewery.objects.get(id=request.user.id)
        return render(request, "users/web/admin/templates/change_password.html",
                      {'login_user': login_user})

    def post(self, request):
        login_user = Brewery.objects.get(id=request.user.id)
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
                    return render(request, "brewery/web/admin/templates/change_password.html",
                                  {'msg': msg, 'login_user': login_user, 'status': 'success'})

                else:
                    msg = 'Please Enter Correct Old Password'
                    return render(request, "brewery/web/admin/templates/change_password.html",
                                  {'msg': msg, 'login_user': login_user, 'status': 'error'})
            else:
                msg = 'User Is Not Registered'
                return render(request, "brewery/web/admin/templates/change_password.html",
                              {'msg': msg, 'status': 'error'})

        except:
            msg = "Please Fill Valid Information"
            return render(request, "users/web/admin/templates/change_password.html", {'msg': msg, 'status': 'error'})

class Offers(View):
	@method_decorator(login_required(login_url='/web/brewery/login/'))
	def get(self, request):
		return render(request,"brewery/web/admin/templates/offers.html", {"page":"OFFERS"})

	@method_decorator(login_required(login_url='/web/brewery/login/'))
	def post(self, request):
		try:
			data = request.POST
			user = request.user
			if request.method == 'POST':
				offer_title = data["offer_title"]
				offer_desc = data["offer_desc"]
				offer_image = request.FILES["offer_image"]
				start_date = datetime.strptime(data["start_date"], '%m-%d-%Y')
				end_date = datetime.strptime(data["end_date"], '%m-%d-%Y')

				user_id = user
				if not user_id:
					return render(request, "brewery/web/admin/templates/offers.html", {'msg': "Please enter valid data" , 'status': 'error'})
				print(user_id)
				if start_date > end_date:
					print("hello")
					return render(request, "brewery/web/admin/templates/offers.html", {'msg': "Start Date must be smaller than End Date" , 'status': 'error'})

				obj = Offer(offer_title=offer_title, offer_desc=offer_desc, 
								  offer_image=offer_image, start_date=start_date,
								  end_date=end_date, user_id=user_id, brewery_owner=user.id)
				obj.save()
				print(obj,"offers")
				return render(request, "brewery/web/admin/templates/offers.html", {'msg': "Your Offer has been created successfully" , 'status': 'success'})
		except Exception as e:
			print(e)
			return render(request, "brewery/web/admin/templates/offers.html", {'msg': str(e), 'status': 'error'})








