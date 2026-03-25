from django.urls import path
from .views import blog, index, post_detail, search, post_update, post_delete, post_create, contact, add_comment, \
    gallery

urlpatterns = [
    path('blog/', blog, name='blog'),
    path('', index, name='index'),
    path('post/<int:id>/', post_detail, name='post-detail'),
    path('search/', search, name='search'),
    path('create/', post_create, name='post_create'),
    path('post/<int:id>/update/', post_update, name='post_update'),
    path('post/<int:id>/delete/', post_delete, name='post_delete'),
    path('contact/', contact, name='contact'),
    path('gallery/', gallery, name='gallery'),
    path('add_comment/<int:id>/', add_comment, name='add_comment')
]
