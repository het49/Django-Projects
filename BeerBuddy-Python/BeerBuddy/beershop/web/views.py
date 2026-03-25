import csv

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from users.models import User
from beershop.models import UserFavourite, Rating, BeerDetail
from event.models import UserInvites, BeerCheckIn, CheckOutImage, Event
from beershop.web.serializers import UserFavouritiesSerializer, UserFeedbackSerializer, UserInvitesSerializer, \
    BeerCheckInImageSerializer


class CheckIn(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        user_checkin_list = BeerCheckIn.objects.all().order_by('-checkin_at')
        star_total = 5
        star_percentage = 0
        user_checkin__rating_list=[]
        for user_checkin in user_checkin_list:
            star_percentage = (user_checkin.user_beer_ratings / star_total) * 100
            user_checkin.star_percentage=star_percentage
            user_checkin__rating_list.append(user_checkin)
        return render(request, "beershop/web/admin/templates/check-in.html",
                      {'user_checkin_list': user_checkin__rating_list,  "nbar": "check-in"})

    def post(self, request):
        return redirect("/web/beershops/check-in/")


class CkeckInDownloadCsvView(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="checkin_users.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Phone No', 'Email ID', 'Location', 'Beer Shop'])

        beer_checkins = BeerCheckIn.objects.all().values_list('user__first_name', 'user__phone_no', 'user__email',
                                                              'beer__vicinity', 'beer__name')
        for beer_checkin in beer_checkins:
            writer.writerow(beer_checkin)

        return response


class ChangeCheckInStatus(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        id = request.POST.get('id', False)
        try:
            checkin_obj = BeerCheckIn.objects.get(id=id)
        except:
            return JsonResponse({'result': 2})
        if checkin_obj:
            if checkin_obj.status:
                checkin_obj.status = False
            else:
                checkin_obj.status = True
            checkin_obj.save()
        return JsonResponse({'result': checkin_obj.status})


class Userfavourites(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        userid = request.POST.get('id')
        user_obj = User.objects.get(id=userid)
        user_favourites_obj = UserFavourite.objects.filter(user=user_obj, status=True)
        user_favourites = UserFavouritiesSerializer(user_favourites_obj, many=True)
        if user_favourites.data:
            result = user_favourites.data
            status = 'success'
        else:
            result = ''
            status = 'error'

        return JsonResponse({'result': result, 'status': status})


class UserFeedback(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        userid = request.POST.get('id')
        beerid = request.POST.get('bid')
        user_obj = User.objects.get(id=userid)
        beer_obj = BeerDetail.objects.get(id=beerid)
        user_feedback_obj = Rating.objects.filter(user=user_obj, beer_shop=beer_obj)
        user_feedbacks = UserFeedbackSerializer(user_feedback_obj, many=True)

        if user_feedbacks.data:
            result = user_feedbacks.data
            status = 'success'
        else:
            result = ''
            status = 'error'

        return JsonResponse({'result': result, 'status': status})


class GetCkeckOutImages(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request, pk):
        user_obj = User.objects.get(id=pk)
        beercheckin_obj = BeerCheckIn.objects.filter(user=user_obj, images__is_delete=False)
        if beercheckin_obj.exists():
            beercheckout_images = BeerCheckInImageSerializer(beercheckin_obj[0].images.all(),
                                                             context={'request': request}, many=True)
            if beercheckout_images.data:
                result = beercheckout_images.data
            else:
                result = ''
        else:
            result = ''
        return render(request, "beershop/web/admin/templates/images.html",
                      {"beercheckout_obj": result, 'user_obj': user_obj, 'beercheckin_obj': beercheckin_obj})


class UserInvitee(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        userid = request.POST.get('id')
        beerid = request.POST.get('bid')
        user_obj = User.objects.get(id=userid)
        beer_obj = Event.objects.get(id=beerid)
        user_invitee_obj = UserInvites.objects.filter(user=user_obj, event=beer_obj)
        user_invites = UserInvitesSerializer(user_invitee_obj, many=True)
        if user_invites.data:
            result = user_invites.data
            status = 'success'
        else:
            result = ''
            status = 'error'

        return JsonResponse({'result': result, 'status': status})


class DeletCheckOutImageView(View):

    def post(self, request):
        ids = request.POST['ids']
        id_for_delete = ids.split(",")

        for id in id_for_delete:
            try:
                image_obj = CheckOutImage.objects.get(id=id)
            except:
                return JsonResponse({'result': 2})
            if image_obj:
                image_obj.is_delete = True
                image_obj.save()
            return JsonResponse({'result': image_obj.is_delete})
