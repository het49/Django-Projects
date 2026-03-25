from django.db import models
from users.models import User
from event.models import BeerCheckIn

# Create your models here.


class Message(models.Model):
    MESSAGE_TYPE_CHOICE = (
        ('accepted', 'Accepted'),
        ('rejected', 'Declined'),
        ('pending', 'Pending'),
        ('cancel', 'Cancel'),
        ('other', 'Other'),
        ('cron-first', 'Cron-First'),
        ('cron-second', 'Cron-Second'),
    )
    MESSAGE_TITLE_CHOICE = (
        ('invite', 'Invite'),
        ('friend', 'Friend'),
        ('checkin', 'Checkin'),
        ('event', 'Event'),
        ('cron-checkout', 'Cron-Checkout'),
        ('offers', 'Offers')

    )

    title = models.CharField(
        max_length=80, choices=MESSAGE_TITLE_CHOICE, default="other")
    type = models.CharField(
        max_length=80, choices=MESSAGE_TYPE_CHOICE, default="other")
    message_title = models.TextField(null=True, blank=True)
    text_message = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'message'


class Notification(models.Model):
    NOTIFICATION_STATUS_CHOICE = (
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('delete', 'Delete'),
    )
    USER_STATUS_CHOICE = (
        ('accepted', 'Accepted'),
        ('rejected', 'Declined'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(
        User, related_name='noti_user', on_delete=models.CASCADE,default="")
    message = models.CharField(max_length=1000, blank=False)
    title_user = models.CharField(max_length=30, null=True, blank=True)
    title_base = models.CharField(max_length=30, null=True, blank=True)
    type_base = models.CharField(max_length=30, null=True, blank=True)
    sender_id = models.ForeignKey(
        User, related_name='noti_sender_user', on_delete=models.CASCADE,default="")
    obj_id = models.IntegerField(blank=False)
    status = models.CharField(
        max_length=30, choices=NOTIFICATION_STATUS_CHOICE, default="unread")
    user_status = models.CharField(
        max_length=30, choices=USER_STATUS_CHOICE, blank=True, null=True)
    like = models.BooleanField(default=False)
    checkin_id = models.IntegerField(default=0)
    like_notification_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(
        'self', auto_now=True, auto_now_add=False)

    def __str__(self):
        return str(self.message)

    class Meta:
        db_table = 'notification'

# class Like_checkin(models.Model):
#     user = models.ForeignKey(User, related_name='like_user',on_delete=models.CASCADE) # friend who like the checkin 
#     checkin_id = models.ForeignKey(BeerCheckIn,related_name='beer_checkinid',on_delete=models.CASCADE)
#     like_notification_id = models.ForeignKey(Notification,related_name='like_notification',on_delete=models.CASCADE)
#     # like = models.BooleanField(default=False)

#     def __str__(self):
#         return str(self.id) + "-" + str(self.user) 

#     class Meta:
#         db_table = 'like_checkin'

