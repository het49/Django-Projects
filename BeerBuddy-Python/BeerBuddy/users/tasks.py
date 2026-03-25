import string
# from celery import shared_task
from event.models import Event, UserInvites, BeerCheckIn
from users.models import User
from notification.models import Message, Notification
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from base.utils.utilities import send_notification, create_notification


def checkin_user():
    event_active = Event.objects.filter(is_active=True)
    check_in_time = datetime.now() + timedelta(hours=-2)
    print(check_in_time,"check_in_time")
    check_in_time = check_in_time.replace(second=0, microsecond=0)
    print('*'*50)
    print('Checking all checkins for before below timing')
    print(check_in_time)
    if event_active.exists():
        print('Active events exists_in')
        for event in event_active:
            print('Processing event: ' + str(event.id))
            beer_checkin_obj = BeerCheckIn.objects.filter(
                event=event, status=True)  # less than 2 hours from now
            if beer_checkin_obj.exists():
                print('Checkin exists for event '+str(event.id))
                print('Filetering further')
                beer_checkin_obj = beer_checkin_obj.filter(
                    checkin_at__lte=check_in_time)
                if beer_checkin_obj.exists():
                    admin_obj = User.objects.filter(groups__name='admin')
                    for checkin_user in beer_checkin_obj:
                        print('Processing beer checkin: ' +
                              str(checkin_user.id))
                        print('Notification count for ' + str(checkin_user.id) +
                              ' is ' + str(checkin_user.notification_count))
                        sender_obj = admin_obj[0]
                        sender_id = sender_obj.id
                        sender_profile = request.build_absolute_uri(
                            admin_obj[0].profile_img.url) if admin_obj[0].profile_img else ""
                        receiver_obj = checkin_user.user
                        obj_id = checkin_user.event.id
                        notification_type = 4  # 1st checkout ###
                        if checkin_user.notification_count == None:  # For first time checking
                            checkin_user.notification_count = 1
                            checkin_user.save()
                            message_obj = Message.objects.get(
                                title="cron-checkout", type="cron-first")
                            message = message_obj.text_message.format(
                                beershop=checkin_user.beer.name)
                            message_title = message_obj.message_title
                            notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                                                                  title_base="cron-checkout", type_base="cron-first",
                                                                  title_user=message_title, status="delete",
                                                                  )
                        # elif checkin_user.notification_count == "1": ## for second time checking
                        #     checkin_user.notification_count = 2
                        #     checkin_user.status = False
                        #     checkin_user.save()
                        #     event.is_active = False
                        #     event.save()
                        #     message_obj = Message.objects.get(title="cron-checkout", type="cron-second")
                        #     message = message_obj.text_message.format(beershop = checkin_user.beer.name)
                        #     message_title = message_obj.message_title
                        #     notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                        #                                           title_base="cron-checkout", type_base="cron-second",
                        #                                           title_user=message_title, status="unread"
                        #                                           )
                            try:
                                send_notification(receiver_obj, notification_id, notification_type, message,
                                                  message_title, sender_profile, sender_id, obj_id=str(checkin_user.beer.id))
                                print('Notification Sent to user_in')
                            except:
                                print('Notification Exception for ' +
                                      str(checkin_user.id))
                                pass
                else:
                    print('No checkin before scheduled time')
            # else:
            #     event.is_active = False
            #     event.save()


def checkout_user():
    check_in_time = datetime.now() + timedelta(hours=-4)
    check_in_time = check_in_time.replace(second=0, microsecond=0)
    print('*'*50)
    print('Checking all checkins for before below timing')
    print(check_in_time)
    beer_checkin_obj = BeerCheckIn.objects.filter(
        status=True, checkin_at__lte=check_in_time)
    if beer_checkin_obj.exists():
        print('Active events exists_out')
        admin_obj = User.objects.filter(groups__name='admin')
        for checkin_user in beer_checkin_obj:
            print('-'*20)
            print('Processing check-in '+str(checkin_user.id))
            print('Checkin user notification count is ' +
                  str(checkin_user.notification_count))
            if checkin_user.notification_count == '1':  # For first time checking
                print('Sending notification to respective user')
                sender_obj = admin_obj[0]
                sender_id = sender_obj.id
                sender_profile = request.build_absolute_uri(
                    admin_obj[0].profile_img.url) if admin_obj[0].profile_img else ""
                receiver_obj = checkin_user.user
                obj_id = checkin_user.event.id
                notification_type = 3  # checkout ###
                message_obj = Message.objects.get(
                    title="cron-checkout", type="cron-second")
                message = message_obj.text_message.format(
                    beershop=checkin_user.beer.name)
                message_title = message_obj.message_title
                notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
                                                      title_base="cron-checkout", type_base="cron-second",
                                                      title_user=message_title, status="unread"
                                                      )
                try:
                    send_notification(receiver_obj, notification_id, notification_type, message,
                                      message_title, sender_profile, sender_id)
                    print('Notification sent to checkin _out ' + str(checkin_user.id))
                    checkin_user.event.is_active = False
                except:
                    print('Notification exception in checkin ' +
                          str(checkin_user.id))
                    pass
        beer_checkin_obj.update(status=False)

    notification_obj = Notification.objects.filter(
        title_base="invite", type_base="pending", created_at__lte=check_in_time)
    if notification_obj.exists():
        notification_obj.update(status="delete")
