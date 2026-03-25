from rest_framework import serializers
from notification.models import Notification


class GetNotificationSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="created_at")
    notification_id = serializers.IntegerField(source="id")
    id = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="sender_id.id")
    title = serializers.CharField(source="title_user")
    user_profile = serializers.SerializerMethodField()
    notification_type = serializers.SerializerMethodField() 

    class Meta:
        model = Notification
        fields = ('date', 'id', 'title', 'message', 'notification_id',
                  'user_id', 'user_profile', 'notification_type', 'user_status','like','checkin_id')

    def get_user_profile(self, obj):
        if obj.sender_id.profile_img:
            request = self.context.get('request')
            profile_img = obj.sender_id.profile_img.url
            return request.build_absolute_uri(profile_img)
        else:
            profile_img = ""
            return profile_img

    def get_notification_type(self, obj):
        if obj.title_base == "friend":
            if obj.type_base == "pending":
                return 0
            elif obj.type_base == "accepted" or "rejected":
                return 3

        if obj.title_base == "invite":
            if obj.type_base == "pending":
                return 1
            elif obj.type_base == "accepted" or "rejected":
                return 3

        if obj.title_base == "checkin":
            return 2

        if obj.title_base == "event":
            return 3

        if obj.title_base == "cron-first"or "cron-second":
            return 3

    def get_id(self, obj):
        if obj.title_base == "friend":
            return obj.sender_id.phone_no if obj.sender_id.phone_no else obj.sender_id.email
        else:
            return "" if obj.obj_id is None else str(obj.obj_id)


class ReadNotificationSerializer(serializers.Serializer):
    read_option = serializers.CharField()
    notification_id = serializers.CharField(required=False)


class DeleteNotificationSerializer(serializers.Serializer):
    delete_option = serializers.CharField()
    notification_id = serializers.CharField(required=False)

class CheckInLikeSerializer(serializers.Serializer):
    notification_id=serializers.CharField(required=False)
    
    pass
