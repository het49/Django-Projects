from django.urls import path
from notification.api import views

app_name = 'event'

urlpatterns = [
    ## Signup and profile URL
    path('notifications/',views.NotificationAPIView.as_view(),name='notifications'),
    path('delete_notifications/',views.DeleteNotificationAPIView.as_view(),name='delete-notifications'),
    path('read_notifications/',views.ReadNotificationAPIView.as_view(),name='read-notifications'),


]


