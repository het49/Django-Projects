from django.urls import path
from base.staticcontent.views import StaticDetailView

from . import views

app_name = 'users'

urlpatterns = [
    # Signup and profile URL
    path('country/', views.CountryAPIView.as_view(), name='country'),
    path('register/', views.UserCreateAPIView.as_view(), name='register'),
    path('verify-passcode/', views.UserVerifyPasscodeAPIView.as_view(),
         name='verify-passcode'),
    path('login/', views.UserLoginAPIView.as_view(), name='login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='logout'),
    path('forgot/password/', views.RequestForgotPasswordAPIView.as_view(),
         name='request-forgot-password'),
    path('reset/password/', views.VerifyForgotPasswordAPIView.as_view(),
         name='reset-forgot-password'),
    path('change/password/', views.ResetPasswordAPIView.as_view(),
         name='change-password'),
    path('forget_verify_passcode/', views.VerifyForgetPasscodeAPIView.as_view(),
         name='forget-verify-passcode'),
    path('edit_profile/', views.ProfileUpdateAPIView.as_view(), name='profile'),
    path('get_access_token/', views.GetAccessTokenAPIView.as_view(),
         name='get_access_token'),
    path('social_phone_update/', views.SocialPhoneUpdateAPIView.as_view(),
         name='social_phone_update'),
    path('verify_social_passcode/', views.SocialVerifyPasscodeAPIView.as_view(),
         name='verify-social-passcode'),

    # Beer Type and details URL

    path('contact_list/', views.UserContactListAPIView.as_view(), name='contact_list'),
    path('friend_request/', views.UserFriendAPIView.as_view(), name='friend-request'),
    path('friend_search/', views.FriendSearchAPIView.as_view(), name='friend-search'),
    path('user_settings/', views.UserSetting.as_view(), name='user-setings'),
    path('other_user_profile/<int:pk>/',
         views.OtherUserProfile.as_view(), name='other-user-profile'),
    path('resend_otp/', views.ResentOTP.as_view(), name='resend-otp'),
    path('page/<slug>/', StaticDetailView.as_view(), name='static-page'),
    path('checkedin_buddies/', views.UserCheckedInBuddyAPIView.as_view(),
         name='checkedin_buddies'),
    path('app_version/', views.AppVersionAPIView.as_view(), name='app_version')
]
