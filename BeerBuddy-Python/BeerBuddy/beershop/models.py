from django.db import models
from django_mysql.models import JSONField
from users.models import User
from BeerBuddy.storage_backends import TestStorage
# Create your models here.


class BeerType(models.Model):
    name = models.CharField(max_length=80, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = 'beer_type'


class BeerDetail(models.Model):
    geometry = JSONField(default=dict)
    google_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255, null=True, blank=True)
    icon = models.TextField(null=True, blank=True)
    formatted_address = models.TextField(null=True, blank=True)
    photos = JSONField()
    place_id = models.CharField(max_length=255, null=True, blank=True)
    plus_code = JSONField()
    reference = models.CharField(max_length=255, null=True, blank=True)
    scope = models.CharField(max_length=80, null=True, blank=True)
    types = models.ManyToManyField(BeerType, related_name='beer_type')
    vicinity = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    brewery = models.ForeignKey(User, null=True, blank=True, related_name='brewery_user', on_delete=models.CASCADE)

    # def __str__(self):
    #     return str(self.place_id)
 

    class Meta:
        db_table = 'beer_detail'


class CheckOutImage(models.Model):
    checkout_image = models.ImageField(
        storage=TestStorage(), blank=True, null=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

# class BeerCheckIn(models.Model):
#     user = models.ForeignKey(User, related_name='checkin_user', on_delete=models.CASCADE)
#     beer = models.ForeignKey(BeerDetail, related_name='beer_checkin', on_delete=models.CASCADE)
#     checkin_at = models.DateTimeField(auto_now=False, auto_now_add=True)
#     message = models.CharField(max_length=255, null=True, blank=True)
#     status = models.BooleanField(default=True)
#     updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
#     images = models.ManyToManyField(CheckOutImage)
#     def __str__(self):
#         return str(self.checkin_at)
#
#     @property
#     def user_beer_ratings(self):
#         rating_obj = Rating.objects.filter(user=self.user, beer_shop=self.beer)
#         if rating_obj.exists():
#             avg_rating = rating_obj.aggregate(Avg('rating'))['rating__avg']
#         else:
#             avg_rating = 0
#         return avg_rating
#
#     class Meta:
#         db_table = 'beer_checkin'


class UserFavourite(models.Model):
    beer_shop = models.ForeignKey(
        BeerDetail, related_name='fav_beer_shop', on_delete=models.CASCADE,default="")
    user = models.ForeignKey(
        User, related_name='fav_user', on_delete=models.CASCADE,default="")
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        db_table = 'user_favourite'


class Rating(models.Model):
    beer_shop = models.ForeignKey(
        BeerDetail, related_name='rating_beer_shop', on_delete=models.CASCADE,default="")
    rating = models.FloatField(default=0.00)
    feedback = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='user',
                             on_delete=models.CASCADE,default="")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return str(self.rating)

    class Meta:
        db_table = 'user_rating'


class BeerPlacesDetail(models.Model):
    location = JSONField()
    category = models.CharField(max_length=50)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.location)

    class Meta:
        db_table = 'beer_places'


class ConfigParam(models.Model):
    config = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.config)

    class Meta:
        db_table = 'config_param'
