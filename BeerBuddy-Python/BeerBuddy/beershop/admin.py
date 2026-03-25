from django.contrib import admin
from beershop.models import *
# Register your models here.
class BeerDetailAdmin(admin.ModelAdmin):
    list_display = ['id','name','google_id','vicinity','place_id', 'brewery']
    search_fields = ['name','place_id']
    list_per_page = 20

class BeerTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_per_page = 20

class UserFavouriteAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    def beer_shop(self):
        return self.beer_shop.name
    list_display = [user,beer_shop,'status']
    search_fields = ['user__username','beer_shop__name','location']
    list_per_page = 20



class RatingAdmin(admin.ModelAdmin):

    def user(self):
        return self.user.username

    def beer_shop(self):
        return self.beer_shop.name

    list_display = [user,'feedback',beer_shop]
    search_fields = ['user__username','beer_shop__name']
    list_per_page = 20



admin.site.register(BeerDetail,BeerDetailAdmin)
admin.site.register(BeerType,BeerTypeAdmin)

admin.site.register(UserFavourite,UserFavouriteAdmin)
admin.site.register(Rating,RatingAdmin)
admin.site.register(CheckOutImage)
admin.site.register(BeerPlacesDetail)
admin.site.register(ConfigParam)