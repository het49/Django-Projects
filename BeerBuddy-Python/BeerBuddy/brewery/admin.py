from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Brewery)
class BreweryAdmin(admin.ModelAdmin):
    list_display = ['id', 'email']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'offer_title']
    readonly_fields = ["start_date", "end_date","brewery_owner"]

