from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *


app_name = 'event'
urlpatterns = [
            path('event_management/', EventManagement.as_view(), name='event_management'),
            path('event_status/', ChangeEventStatus.as_view(), name='event_status'),
            path('event_details/<int:pk>', EventDetails.as_view(), name='event_details'),
            # path('event_details/', GetEventDetails.as_view(), name='event_details'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)