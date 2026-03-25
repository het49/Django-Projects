from django.urls import path
from base.staticcontent.views import StaticDetailView
from event.api import views

app_name = 'event'

urlpatterns = [
    ## event URL
    path('invites/',views.InvitiesAPIView.as_view(),name='invites'),
    path('delete/event/<int:pk>/',views.EventDeleteAPIView.as_view(),name='delete-event'),
    path('user/events/',views.EventAPIView.as_view(),name='user_events'),
    path('event/details/',views.EventDetailAPIView.as_view(),name='event_detail'),
    path('event/decline/',views.EventDeclineAPIView.as_view(),name='event_decline'),
    path('event/remove/',views.EventRemoveAPIView.as_view(),name='event_remove'),
    path('event/comment/',views.EventCommentAPIView.as_view(),name='event_comment'),

]


