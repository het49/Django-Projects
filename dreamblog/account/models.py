from django.db import models
from django.conf import settings


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to='image1')
    contact = models.IntegerField()
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
