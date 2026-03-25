from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import *


app_name = 'users'
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashBoard.as_view(), name='dashboard'),
    path('user_managment/', UserManagement.as_view(), name='user_managment'),
    path('exportuserlist/', UserDownloadCsvView.as_view(), name='exportuserlist'),
    path('friend_list/', GetBeerUserConnection.as_view(), name='friend-list'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
    path('logout/', views.logout, name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('changeuserstatus/', ChangeUserStatus.as_view(), name='users'),
    path('userdetails/', GetUserDetails.as_view(), name='userdetails'),
    path('privacy-policy/', PrivacyPolicy.as_view(), name='privacy_policy'),
    path('edit-privacy-policy/<int:pk>/', EditPrivacyPolicy.as_view(), name='edit-privacy_policy'),
    path('terms-condition/', TermsCondition.as_view(), name='term_conditionView'),
    path('edit-terms-condition/<int:pk>/', EditTermsCondition.as_view(), name='edit_term_conditionView'),
    path('chart-data/', PieChartView.as_view(), name='chart-data'),
    path('delete/<int:pk>', DeleteUserView.as_view(), name='delete'),
    path('brewery_management/', BreweryManagement.as_view(), name='brewery_management'),
    path('brewery_registration/', BreweryRegister.as_view(), name='brewery_registration'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)