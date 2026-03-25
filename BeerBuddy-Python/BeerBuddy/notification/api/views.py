from datetime import datetime

from base.utils.utilities import (validate_headers, success_response,error_response)
from notification.api.serializers import GetNotificationSerializer,DeleteNotificationSerializer,ReadNotificationSerializer
from notification.models import Notification
from rest_framework.views import APIView
from users.api.permissions import IsAllowed
from users.models import User
from collections import OrderedDict
from orderedset import OrderedSet

class NotificationAPIView(APIView):
    permission_classes = [IsAllowed]

    def get(self, request, *args, **kwargs):
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)

        validate_headers(platform, device_id, app_version)
        return_data = []
        user_obj = request.user
        notification_obj = Notification.objects.filter(user = user_obj).exclude(status = "delete").order_by("-created_at")
        notification_obj.update(status = "read")
        notification_list =[]
        if notification_obj.exists():
            date_list = notification_obj.values_list('created_at__date', flat=True)
            for date_obj in OrderedSet(date_list):
                data = {}
                date = date_obj.strftime("%d/%m/%Y")
                data['date'] = date
                data['notification'] = GetNotificationSerializer(notification_obj.filter(created_at__date = date_obj),many =True,context={'request': request}).data
                notification_list.append(data)

            notification_list.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)
            return_data=notification_list
        else:
            pass
        message='success'
        return success_response(message, return_data)


class DeleteNotificationAPIView(APIView):
    permission_classes = [IsAllowed]

    def put(self, request, *args, **kwargs):
        data = request.data
        serializer = DeleteNotificationSerializer(data=data)
        platform = request.META.get('HTTP_PLATFORM', None)
        device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
        device_id = request.META.get('HTTP_DEVICE_ID', None)
        app_version = request.META.get('HTTP_APP_VERSION', None)

        validate_headers(platform, device_id, app_version)
        user_obj = request.user
        delete_option = data["delete_option"]
        if delete_option == "single":
            notification_obj = Notification.objects.filter(id=data['notification_id']).exclude(status = "delete")
        else:
            notification_obj = Notification.objects.filter(user=user_obj).exclude(status = "delete")

        if notification_obj.exists():
            notification_obj.update(status="delete")
            return success_response(message="Notification deleted successfully.",
                                         data={})
        else:
            return error_response(message="No notification found to delete.", data={})


class ReadNotificationAPIView(APIView):
    permission_classes = [IsAllowed]

    def put(self,request,*args,**kwargs):
        data = request.data
        serializer = ReadNotificationSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)
            read_option = data["read_option"]
            user_obj = request.user
            validate_headers(platform, device_id, app_version)
            if read_option == "single":
                notification_obj = Notification.objects.filter(id=data['notification_id'])
            else:
                notification_obj = Notification.objects.filter(user = user_obj)

            if notification_obj.exists():
                notification_obj.update(status='read')
                return success_response(message="Notification Read successfully.",data={})
            else:
                return success_response(message="No notification found to Read.", data={})
