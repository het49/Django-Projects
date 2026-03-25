from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import *

app_name = 'brewery'

urlpatterns = [
    path('brewery_dashboard/',dashboard, name='brewery_dashboard'),
    path('profile/',BreweryProfileView.as_view(), name='brewery_profile'),
    path('login/',LoginView.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('changepassword/',Change_Password.as_view(), name='changepassword'),
    path('offers/',Offers.as_view(), name='offers'),
    path('offers_status/<int:offer_id>',OfferStatus, name='offers_status'),
    path('error/',csrf_failure, name='error'),



    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)