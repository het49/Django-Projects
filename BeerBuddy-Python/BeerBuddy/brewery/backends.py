from django.contrib.auth import get_user_model
from brewery.models import Brewery
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password

User = get_user_model()
# from django.db.models import Q

UserModel = get_user_model()
class EmailBackend:
	def authenticate(self, request, email=None, password=None,type = None, **kwargs):
		try:
			if type=="BREWERY":
				user = Brewery.objects.get(email=email, type="BREWERY")
			else:
				user = User.objects.get(email=email, type="NORMALUSER")

			pwd_valid = user.check_password(password)

			if pwd_valid == False :
				return None
			return user
		except Exception as e:
			print(e,"Error")
			return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except Exception as e:
			print(e)
			return None