from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


app_name = 'beershop'
urlpatterns = [
    path('userfavourites/', Userfavourites.as_view(), name='user-favourites'),
    path('check-in/', CheckIn.as_view(), name='check-in'),
    path('exportcheckinuser/', CkeckInDownloadCsvView.as_view(), name='export-checkin-user'),
    path('changecheckinstatus/', ChangeCheckInStatus.as_view(), name='change-checkin-status'),
    path('userinvites/', UserInvitee.as_view(), name='user-invites'),
    path('userfeedbacks/', UserFeedback.as_view(), name='user-feedbacks'),
    path('checkout_images/<int:pk>', GetCkeckOutImages.as_view(), name='checkout-images'),
    path('delete_images/', DeletCheckOutImageView.as_view(), name='delete-images'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)