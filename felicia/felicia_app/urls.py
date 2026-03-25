from django.conf import settings
from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from .import views
from .views import PriceListing
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('invoice/<orderid>/',views.invoice,name='invoice'),
    # path('home/',views.home,name='home'),
    path('test/',views.test,name='test'),
    path('login/', views.login, name='login'),
    path('logout/', views.login, name='logout'),
    path('register/', views.register, name='register'),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("checkout/", views.checkout, name="Checkout"),
    path("checkoutform/", views.checkoutform, name="Checkoutform"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    path("activation/<int:user_id>/",views.activation,name="activation"),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='password_reset.html'),name='reset_password'),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'),name='reset_password_complete'),
    path('products/<int:myid>',views.productView,name='products'),
    path('placeorder/',views.placeorder,name="placeorder"),
    path('category/',views.cat_view,name='category'),
    path('subcategory/<catid>',views.subcat,name='subcategory'),
    path('testproduct/<subid>',views.testproduct,name='testproduct'),
    path('allprod/<subid>/',views.allprod,name='allprod'),
    path("search/", views.search, name="Search"),
    path("allcat/",views.all_category,name="allcat"),
    path('pricelist/', views.PriceList),
    path("price_listing/", PriceListing.as_view(),name='listing'),
    path("ajax/price/", views.getPrice, name = 'get_price'),
    path("ajax/product_name/",views.getProduct_name, name = 'get_product_name'),
    path('aboutus/', views.aboutus,name="aboutus"),
    path('contactus/', views.contactus,name="contactus"),
    path('newarrivals/', views.newarrivals),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += staticfiles_urlpatterns()
    