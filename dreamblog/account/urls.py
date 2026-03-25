from django.urls import path
from .views import registration, addprofile, updateprofile

urlpatterns = [
    path('registration/', registration, name='registration'),
    path('addprofile/', addprofile, name='addprofile'),
    path('updateprofile/<int:id>/', updateprofile, name='updateprofile')
]
