from django.contrib import admin
from notification.models import Message,Notification
# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    list_display = ['title','type','message_title','text_message','is_active',]
    search_fields = ['title','message_title']
    list_editable =['is_active']
    list_per_page = 20
#
class NotificationAdmin(admin.ModelAdmin):
    def user(self):
        return self.user.username
    list_display = ['id',user,'sender_id','obj_id','message','status','user_status']
    search_fields = ['user__username','message__username']
    list_per_page = 20

admin.site.register(Message,MessageAdmin)
admin.site.register(Notification,NotificationAdmin)
