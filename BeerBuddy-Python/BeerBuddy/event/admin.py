from django.contrib import admin
from event.models import *
# Register your models here.
class UserInvitesAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    def invitee(self):
        return self.invitee.username

    def event(self):
        return self.event.id

    list_display = [user,invitee,event,'location','status']
    search_fields = ['user__username','invitee__username','location']
    list_per_page = 20

class EventAdmin(admin.ModelAdmin):

    list_display = ['id', 'name','is_active','is_delete','created_at','updated_at']
    search_fields = ['name']
    list_editable = ['is_active']
    list_per_page = 20

class BeerCheckInAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    def beer(self):
        return self.beer.name
    list_display = ['id', user,beer,'checkin_at','status']
    search_fields = ['user__username','beer__name','checkin_at','status']
    list_per_page = 20


admin.site.register(UserInvites,UserInvitesAdmin)
admin.site.register(Event,EventAdmin)
admin.site.register(BeerCheckIn,BeerCheckInAdmin)
admin.site.register(EventComments)