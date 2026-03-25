from django.urls import path
from base.staticcontent.views import StaticDetailView
from beershop.api import views

app_name = 'beershop'

urlpatterns = [
    ## Beer Type and details URL
    path('add_beerdetail/',views.AddBeerDetailAPIView.as_view(),name='add_beerdetail'),
    path('beer_checkin/',views.BeerCheckInAPIView.as_view(),name='beer_checkin'),
    path('beer_checkout/',views.BeerCheckOutAPIView.as_view(),name='beer_checkout'),
    path('rating/',views.RatingAPIView.as_view(),name='rating'),
    path('user_favourite/',views.UserFavouriteAPIView.as_view(),name='user_favourite'),
    path('find_beers/',views.LocationWiseBeerAPIView.as_view(),name='find_beers'),
    path('save_beers/',views.BeerPlacesSaveAPIView.as_view(),name='save_beers'),
    # path('save_beers/',views.BeerPlacesSaveAPIView.as_view(),name='save_beers'),
    path('like_checkin/',views.CheckInLikeAPIView.as_view(),name='like_checkin'),
    path('nearby_offers/',views.NearbyOffers_FriendCheckinAPIView.as_view(),name='nearby_offers'),

    

]


