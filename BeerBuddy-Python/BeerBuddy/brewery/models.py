from django.db import models
from users.models import User
from django.contrib.auth.models import BaseUserManager
from BeerBuddy.storage_backends import TestStorage, PublicMediaStorage

# Create your models here.
class BreweryManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(type="BREWERY")

    def _create_user(self, email, password, **kwargs):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        username = self.normalize_email(email)
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        kwargs.update({'type': 'BREWERY'})
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **kwargs):
        return self._create_user(email, password, **kwargs)
        # return super(BreweryManager, self).create_user(**kwargs)



class Brewery(User):
    # base_type = User.Types.BREWERY
    objects = BreweryManager()

    class Meta:
    	proxy = True

def offers_upload_func(instance, filename):
    return f"offers/{filename}"   

class Offer(models.Model):
    offer_title = models.CharField(max_length = 50, default = "")
    offer_desc = models.CharField(max_length = 500, default = "")
    # offer_image = models.ImageField(storage=TestStorage(), blank=True, null=True)
    offer_image = models.ImageField(storage=PublicMediaStorage(), upload_to=offers_upload_func, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    user_id = models.ForeignKey(User, null=True, blank=True, related_name='brewery_offers', on_delete=models.CASCADE)  
    brewery_owner = models.IntegerField(default=0)
    expired = models.BooleanField(default = False)
    live = models.BooleanField(default = True)
    

    class Meta:
        db_table = "offers"

    def __str__(self):
        return str(self.user_id) + "-" + self.offer_title