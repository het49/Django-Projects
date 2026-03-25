from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.utils.decorators import method_decorator
from django.views import View

from event.models import Event,UserInvites,BeerCheckIn


class EventManagement(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request):
        event_list = Event.objects.all().order_by('-created_at')
        event_count = event_list.count()
        return render(request, "event/web/admin/templates/event_management.html",{'event_list':event_list,'event_count':event_count,"nbar": "event_management"})


class ChangeEventStatus(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def post(self, request):
        event_id = request.POST.get('id', False)
        try:
            event_obj = Event.objects.get(id=event_id)
        except:
            return JsonResponse({'result': 2})
        if event_obj:
            if event_obj.is_active:
                event_obj.is_active = 0
            else:
                event_obj.is_active = 1
            event_obj.save()
        return JsonResponse({'result': event_obj.is_active})


class EventDetails(View):
    @method_decorator(login_required(login_url='/web/users/login/'))
    def get(self, request,pk):
        event_obj = Event.objects.filter(id=pk)
        invitee_list = UserInvites.objects.filter(event = event_obj[0])
        if invitee_list.exists():
            return render(request, "event/web/admin/templates/event_details.html",{"event_obj":event_obj[0],"invitee_list": invitee_list,"nbar": "event_details"})
        return render(request, "event/web/admin/templates/event_details.html",
                      {"event_obj": event_obj, "invitee_list": invitee_list,
                       "nbar": "event_details"})








