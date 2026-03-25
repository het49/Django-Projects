"""BeerBuddy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import (
handler404
)
# from BeerBuddy import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include("users.api.urls", namespace='users-api')),
    # path('users/', include("users.urls", namespace='users')),
    path('api/events/', include("event.api.urls", namespace='event-api')),
    path('api/beershops/', include("beershop.api.urls", namespace='beershop-api')),
    path('web/users/', include("users.web.urls", namespace='users-web')),
    path('web/events/', include("event.web.urls", namespace='event-web')),
    path('web/beershops/', include("beershop.web.urls", namespace='beershop-web')),
    path('api/notification/', include("notification.api.urls", namespace='notification-api')),
    path('web/brewery/', include("brewery.urls", namespace='brewery-web')),
    path('api/brewery/', include("brewery.api.urls", namespace='brewery-api')),

] 

handler404 = 'BeerBuddy.views.not_found'


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)