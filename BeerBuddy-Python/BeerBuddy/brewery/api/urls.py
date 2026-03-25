from django.urls import path
from base.staticcontent.views import StaticDetailView
from brewery.api import views

app_name = 'brewery'

urlpatterns = [
    ## event URL
    path('nearby_brewery/',views.NearByBreweryAPIView.as_view(),name='nearby_brewery'),
    path('nearby_offers/',views.NearByOffersAPIView.as_view(),name='nearby_offers'),


]


