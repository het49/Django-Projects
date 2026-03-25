from django.db import models                                                                 
from django.db.models import Avg
from users.models import User
from beershop.models import BeerDetail, CheckOutImage, Rating
# Create your models here.


class Event(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # key for event finished
    is_delete = models.BooleanField(default=False)  # key for delete the event
    # key for remove from the event listing
    is_remove = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,default="")
    beer_shop = models.ForeignKey(
        BeerDetail, related_name='invite_beer_shop', on_delete=models.CASCADE,default="")

    def __str__(self):
        return str(self.id)+ "--" +str(self.name)

    class Meta:
        db_table = 'event'


class UserInvites(models.Model):
    INVITE_STATUS_CHOICE = (
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
        ('cancel', 'Cancel'),
    )
    event = models.ForeignKey(
        Event, related_name='event_invites', on_delete=models.CASCADE,default="")
    user = models.ForeignKey(
        User, related_name='sender_user', on_delete=models.CASCADE,default="")
    invitee = models.ForeignKey(
        User, related_name='invitee_user', on_delete=models.CASCADE,default="")
    location = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    # key for remove from the event listing
    is_remove = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30, choices=INVITE_STATUS_CHOICE, default="pending")
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.invitee.id)

    @property
    def invitee_checkin(self):
        checkin_obj = BeerCheckIn.objects.filter(
            event=self.event, user=self.invitee)
        if checkin_obj.exists():
            return checkin_obj[0].checkin_at

    class Meta:
        db_table = 'user_invite'


class BeerCheckIn(models.Model):
    event = models.ForeignKey(
        Event, related_name='checkin_event', on_delete=models.CASCADE,default="")
    user = models.ForeignKey(
        User, related_name='checkin_user', on_delete=models.CASCADE,default="")
    beer = models.ForeignKey(
        BeerDetail, related_name='beer_checkin', on_delete=models.CASCADE,default="")
    checkin_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    user_timestamp = models.CharField(max_length=15, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)
    notification_count = models.CharField(max_length=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    images = models.ManyToManyField(CheckOutImage)

    def __str__(self):
        return str(self.checkin_at)

    @property
    def user_beer_ratings(self):

        rating_obj = Rating.objects.filter(user=self.user, beer_shop=self.beer)
        if rating_obj.exists():
            avg_rating = rating_obj.aggregate(Avg('rating'))['rating__avg']
        else:
            avg_rating = 0
        return avg_rating

    class Meta:
        db_table = 'beer_checkin'


class EventComments(models.Model):
    event = models.ForeignKey(
        Event, related_name='event_comment', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        User, related_name='sender_comment', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.message
