from datetime import datetime, timedelta
from users.api.permissions import IsAllowed
from base.utils.utilities import (validate_headers, success_response, error_response, get_avg_rating, get_favourite,
                                  get_checkout_img, get_user_check_in, get_beer_detail, send_notification,
                                  create_notification)
from rest_framework.views import APIView
from users.models import User
from event.models import UserInvites, Event, BeerCheckIn, EventComments
from beershop.models import BeerDetail
from notification.models import Message, Notification
from event.api.serializers import (GetUserInvitesSerializer, GetUserInvitedSerializer, InvitiesSerializer,
                                   EventListingRecevied, EventListingSender, InvitiesUpdateSerializer, GetUserInvitedEventSerializer,
                                   GetEventCommentsSerializer, GetUserInviteeEventSerializer, EventCommentsSerializer)
from orderedset import OrderedSet
from django.db.models import Q


class InvitiesAPIView(APIView):
	permission_classes = [IsAllowed]

	def get(self, request, *args, **kwargs):
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)

		validate_headers(platform, device_id, app_version)

		req_status = request.GET["status"]
		user_obj = request.user

		if req_status:
			invites_obj = UserInvites.objects.filter(status=req_status)
		else:
			invites_obj = UserInvites.objects.all()
		item = []

		for invites in invites_obj:

			if invites.user == user_obj:
				serializer = GetUserInvitesSerializer(
				    invites, context={"request": request})
				item.append(serializer.data)
			elif invites.invitee == user_obj:
				serializer = GetUserInvitedSerializer(
				    invites, context={"request": request})
				item.append(serializer.data)

		message = "success"
		return success_response(message, item)

	def post(self, request, *args, **kwargs):
		data = request.data
		serializer = InvitiesSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			platform = request.META.get('HTTP_PLATFORM', None)
			device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
			device_id = request.META.get('HTTP_DEVICE_ID', None)
			app_version = request.META.get('HTTP_APP_VERSION', None)
			validate_headers(platform, device_id, app_version)
			return_data = {}
			user_obj = request.user
			beer_shop = data['beer_shop']
			location = data['location']
			user_message = data['message']
			status = data['status']
			if status == 'accepted' or status == 'rejected' or status == 'pending' or status == 'cancel':
				try:
					beer_shop_obj = BeerDetail.objects.get(id=beer_shop)
				except:
					message = "Beer Detail is not available with us."
					return error_response(message, return_data)
				event_exists = False
				new_event_obj = Event.objects.filter(beer_shop=beer_shop_obj, created_by=user_obj, is_active=True,
				                                 is_delete=False)
				if not new_event_obj.exists():
					new_event_obj = Event.objects.create(name=beer_shop_obj.name, created_by=user_obj,
					                                     beer_shop=beer_shop_obj)
				else:
					new_event_obj = new_event_obj[0]
					event_exists = True
				for item in data['invitee']:
					phone_no = item
					try:
						user_invites_obj = User.objects.get(phone_no=phone_no)
					except:
						try:
							user_invites_obj = User.objects.get(email=phone_no)
						except:
							message = "User not registered with us."
							return error_response(message, return_data)
					if not user_obj.id == user_invites_obj.id:
						create_userinvites_obj = True
						if event_exists and status == 'pending':
							userinvites_obj = UserInvites.objects.filter(event=new_event_obj, user=user_obj,
														invitee=user_invites_obj
													)
							if userinvites_obj.exists():
								if userinvites_obj[0].status == "accepted":
									continue
								elif userinvites_obj[0].status == "pending":
									userinvites_obj = userinvites_obj[0]
									create_userinvites_obj = False
						if create_userinvites_obj:
							userinvites_obj = UserInvites.objects.create(event=new_event_obj, user=user_obj,
																			invitee=user_invites_obj, location=location,
																			status=status,
																			message=user_message)
						try:
							message_obj = Message.objects.get(title="invite", type=status)
							sender_obj = user_obj
							message = message_obj.text_message.format(username=sender_obj.first_name,
																		beershop=beer_shop_obj.name)
							receiver_obj = user_invites_obj
							sender_id = user_obj.id
							sender_profile = request.build_absolute_uri(
								user_obj.profile_img.url) if user_obj.profile_img else ""
							obj_id = userinvites_obj.id
							message_title = message_obj.message_title
							notification_type = 1  ### invite ####
							notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
																	title_base="invite", type_base=status,
																	title_user=message_title, checkin_id=0, status="unread",
																	user_status=status)
							print("hellllllllllllllloooo")
							send_notification(receiver_obj, notification_id, notification_type, message,
												message_title, sender_profile, sender_id, str(obj_id))
						except Exception as e:
							print(e)
				# else:
				# 	message = "Your event is already active."
				# 	return error_response(message, return_data)
			else:
				message = "Status is invalid"
				return error_response(message, return_data)

		message = "success"
		return success_response(message, return_data)

	def put(self, request, *args, **kwargs):
		data = request.data
		serializer = InvitiesUpdateSerializer(data=data)

		if serializer.is_valid(raise_exception=True):
			platform = request.META.get('HTTP_PLATFORM', None)
			device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
			device_id = request.META.get('HTTP_DEVICE_ID', None)
			app_version = request.META.get('HTTP_APP_VERSION', None)
			validate_headers(platform, device_id, app_version)
			return_data = {}
			status = data["status"]
			event = data["event_id"]
			user_obj = request.user
			# event_obj = Event.objects.filter(created_by=user_obj, id=event, is_active=True, is_delete=False)
			# if event_obj.exists():
			# 	event_obj.update(is_active=False)
			if status == 'accepted' or status == 'rejected':
				# invites_obj = UserInvites.objects.filter(invitee=user_obj, event_id=event, event__is_delete=False)
				try:
					invites_obj = UserInvites.objects.get(id=event)
				except UserInvites.DoesNotExist:
					message = "Invite does not exists"
					return error_response(message, return_data)
				notification_obj = Notification.objects.filter(
					user=user_obj, obj_id=event)
				if invites_obj is not None:
					if notification_obj.exists():
						if status == "rejected":
							# notification_obj.update(user_status=status, status="delete")
							notification_obj.update(user_status=status)
						else:
							notification_obj.update(user_status=status)
						try:
							message_obj = Message.objects.get(title="invite", type=status)
							sender_obj = invites_obj.invitee
							message = message_obj.text_message.format(username=sender_obj.first_name,
							                                          beershop=invites_obj.event.name)
							receiver_obj = invites_obj.user
							sender_id = invites_obj.invitee.id
							sender_profile = request.build_absolute_uri(invites_obj.invitee.profile_img.url) if \
							invites_obj.invitee.profile_img else ""
							obj_id = invites_obj.event.id
							message_title = message_obj.message_title
							notification_type = 3  ### invite accept/reject ####
							notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
							                                      title_base="invite", type_base=status,
							                                      title_user=message_title, checkin_id=0,status="unread",
							                                      user_status=status)
							# if status == 'accepted':
							send_notification(receiver_obj, notification_id, notification_type, message,
								                message_title, sender_profile, sender_id, str(obj_id))
						except:
							pass
						# invite_obj = invites_obj.first()
						invites_obj.status = status
						invites_obj.save()
						# invite_check = UserInvites.objects.filter(event_id=event, event__is_delete=False,status="accepted")
						# if not invite_check.exists():
						# 	event_check = Event.objects.filter(id=event, is_active=True, is_delete=False)
						# 	if event_check.exists():
						# 		event_check.update(is_delete=True)

			# elif status =='cancel':
			#     user_invite_obj = UserInvites.objects.filter(user=user_obj, event_id=event)
			#     if invites_obj:
			#         invites_obj.update(status=status)
			else:
				message = "Status is invalid"

				return error_response(message, return_data)

		message = "success"

		return success_response(message, return_data)


class EventAPIView(APIView):
	permission_classes = [IsAllowed]

	def get(self, request, *args, **kwargs):
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		time_diff = int(request.GET.get("minutes", 0))
		print(time_diff,"time_diff")
		user_obj = request.user
		return_data = {}
		validate_headers(platform, device_id, app_version)
		invitation = []
		user_invitee = []
		events_obj = Event.objects.filter(created_by=user_obj, is_delete=False,is_remove = False).order_by("-created_at")
		if events_obj.exists():
			print("there")
			# date_list = events_obj.values_list('created_at__date', flat=True)
			# for date_obj in OrderedSet(date_list):
			# 	item = {}
			# 	item['date'] = date_obj.strftime('%d/%m/%Y')
			# 	events = EventListingSender(events_obj.filter(created_at__date=date_obj), many=True,
			# 	                   context={"request": request, "user_obj": user_obj}).data
			# 	events.sort(key=lambda x: x['users_checkin'])
			# 	item['events'] = events
			# 	user_invitee.append(item)
			events = EventListingSender(events_obj, many=True,
                               context={"request": request, "user_obj": user_obj, "time_diff": time_diff}).data
			events_obj = {}
			for event in events:
				item = {}
				date_obj_ = event["date"]
				date_obj = date_obj_.strftime('%d/%m/%Y')
				if date_obj not in events_obj:
					events_obj[date_obj] = []
				events_obj[date_obj].append(event)
			
			for date, event in events_obj.items():
				events.sort(key=lambda x: x['users_checkin'])
				obj = {
					'date': date,
					'events': event
				}
				user_invitee.append(obj)
		user_invitions_obj = UserInvites.objects.filter(invitee=user_obj,
														status="accepted",
														event__is_delete=False,
		                                                # event__is_active=True,
														is_remove = False)
		if user_invitions_obj.exists():
			# date_list = user_invitions_obj.values_list('created_at__date', flat=True)
			# for date_obj in OrderedSet(date_list):
			# 	item = {}
			# 	item['date'] = date_obj.strftime("%d/%m/%Y")
			# 	events = EventListingRecevied(user_invitions_obj.filter(created_at__date=date_obj), many=True,
			# 	                     context={"request": request, "user_obj": user_obj}).data
			# 	events.sort(key=lambda x: x['users_checkin'])
			# 	item['events'] = events
			# 	invitation.append(item)
			events = EventListingRecevied(user_invitions_obj, many=True,
                                 context={"request": request, "user_obj": user_obj, "time_diff": time_diff}).data
			events_obj = {}
			for event in events:
				item = {}
				date_obj_ = event["date"]
				date_obj = date_obj_.strftime('%d/%m/%Y')
				if date_obj not in events_obj:
					events_obj[date_obj] = []
				events_obj[date_obj].append(event)

			for date, event in events_obj.items():
				events.sort(key=lambda x: x['users_checkin'])
				obj = {
					'date': date,
					'events': event
				}
				invitation.append(obj)
				
		if user_invitee:
			user_events = []
			for invite in invitation:
				match = 0
				for event_obj in user_invitee:
					if invite["date"] == event_obj["date"]:
						event_obj["events"].extend(invite["events"])
						match = 1
						break
				if not match:
					user_events.append(invite)
			user_invitee.extend(user_events)
		else:
			user_invitee.extend(invitation)
		
		for event in user_invitee:
			invitation_count = 0
			checkin = 0
			checkout = 0
			for user_checkin in event["events"]:
				if user_checkin["users_checkin"] == 0:
					if invitation_count == 0:
						user_checkin.update(is_title_show = True)
					invitation_count+=1
				if(user_checkin["users_checkin"]==1):
					if checkin == 0:
						user_checkin.update(is_title_show=True)
					checkin +=1
				if(user_checkin["users_checkin"]==2):
					if checkout == 0:
						user_checkin.update(is_title_show=True)
					checkout +=1
		# user_invitee.sort(key=operator.itemgetter('date'), reverse=True)
			event["events"].sort(key=lambda x: x['users_checkin'])
		message = "success"
		user_invitee.sort(key=lambda x: datetime.strptime(x['date'],'%d/%m/%Y'),reverse = True)
		return success_response(message, user_invitee)


class EventDeleteAPIView(APIView):
	permission_classes = [IsAllowed]

	def delete(self, request, pk, *args, **kwargs):
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		validate_headers(platform, device_id, app_version)
		return_data = {}
		event = pk
		user_obj = request.user
		try:
			event_obj = Event.objects.get(id=event, created_by=user_obj)
			event_obj.is_delete = True
			event_obj.save()
			user_invites_obj = UserInvites.objects.filter(user=user_obj, event=event_obj, status="accepted")
			if user_invites_obj.exists():
				for user_invite in user_invites_obj:
					try:
						message_obj = Message.objects.get(title="event", type="other")
						sender_obj = user_invite.user
						message = message_obj.text_message.format(username=sender_obj.first_name,
						                                          beershop=user_invite.event.name)
						receiver_obj = user_invite.invitee
						sender_id = user_invite.user.id
						sender_profile = request.build_absolute_uri(
							user_invite.user.profile_img.url) if user_invite.invitee.profile_img else ""
						obj_id = user_invite.event.id
						message_title = message_obj.message_title
						notification_type = 3  ### event delete ####
						notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
						                                      title_base="invite", type_base="cancel",
						                                      title_user=message_title, checkin_id=0,status="read",
						                                      user_status="cancel")
						send_notification(receiver_obj, notification_id, notification_type, message, message_title,
						                  sender_profile, sender_id, str(obj_id))
					except:
						pass

		except:
			message = "Invalid event id"
			return error_response(message, return_data)

		message = "success"

		return success_response(message, return_data)


class EventDetailAPIView(APIView):
	permission_classes = [IsAllowed]

	def get(self, request, *args, **kwargs):
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		return_data = []

		validate_headers(platform, device_id, app_version)
		event_id = request.GET["event_id"]
		user_obj = request.user
		user_invitation_obj = UserInvites.objects.filter(event_id=event_id, event__is_delete=False)
		if user_invitation_obj.exists():
			invitation = []
			for invited_buddies in user_invitation_obj:
				if invited_buddies.user == user_obj:
					inviteto = GetUserInvitedEventSerializer(user_invitation_obj, context={"request": request},
					                                         many=True).data
					invitation = inviteto
				elif invited_buddies.invitee == user_obj:
					inviteby = GetUserInviteeEventSerializer(invited_buddies, context={"request": request}).data
					inviteto = GetUserInvitedEventSerializer(user_invitation_obj.exclude(invitee=user_obj),
					                                         context={"request": request}, many=True).data
					inviteto.append(inviteby)
					invitation = inviteto

		else:
			message = "No invitation on this event id"
			return success_response(message, return_data)

		message = "success"

		return success_response(message, invitation)


class EventDeclineAPIView(APIView):
	permission_classes = [IsAllowed]

	def put(self, request, *args, **kwargs):
		data = request.data
		serializer = InvitiesUpdateSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			platform = request.META.get('HTTP_PLATFORM', None)
			device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
			device_id = request.META.get('HTTP_DEVICE_ID', None)
			app_version = request.META.get('HTTP_APP_VERSION', None)
			validate_headers(platform, device_id, app_version)
			return_data = {}
			status = data["status"]
			event = data["event_id"]
			user_obj = request.user
			if status == 'rejected':
				invites_obj = UserInvites.objects.filter(invitee=user_obj, event_id=event, event__is_delete=False,
				                                         status="accepted")
				if invites_obj.exists():
					try:
						message_obj = Message.objects.get(title="event", type=status)
						sender_obj = user_obj
						message = message_obj.text_message.format(username=sender_obj.first_name,
						                                          beershop=invites_obj[0].event.name)
						receiver_obj = invites_obj[0].user
						sender_id = user_obj.id
						sender_profile = request.build_absolute_uri(invites_obj[0].invitee.profile_img.url) if \
						invites_obj[
							0].invitee.profile_img else ""
						obj_id = invites_obj[0].event.id
						message_title = message_obj.message_title
						notification_type = 3  ### event decline####
						notification_id = create_notification(sender_obj, receiver_obj, message, obj_id,
						                                      title_base="event", type_base="event decline",
						                                      title_user=message_title, checkin_id=0,status="read",
						                                      user_status=status)
						# notification_id = create_notification(sender_obj, receiver_obj, message, obj_id, status="read",
						#                                       user_status=status)

						send_notification(receiver_obj, notification_id, notification_type, message, message_title,
						                  sender_profile, sender_id, str(obj_id))
					except:
						pass
					invites_obj.update(status=status)
			else:
				message = "Status is invalid"
				return error_response(message, return_data)

			message = "success"
			return success_response(message, return_data)


class EventRemoveAPIView(APIView):
	permission_classes = [IsAllowed]

	def post(self,request):
		data = request.data
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		validate_headers(platform, device_id, app_version)
		return_data = {}
		event_id_list = data["event_id_list"]
		user_obj = request.user
		for event_id in event_id_list:
			try:
				event_obj = Event.objects.get(id= event_id,created_by = user_obj)
				event_obj.is_remove = True
				event_obj.save()
			except:
				try:
					event_obj = UserInvites.objects.get(event__id = event_id,invitee = user_obj)
					event_obj.is_remove = True
					event_obj.save()
				except:
					pass

		message = "success"
		return success_response(message, return_data)


class EventCommentAPIView(APIView):
	permission_classes = [IsAllowed]

	def get(self, request, *args, **kwargs):
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		return_data = []
		validate_headers(platform, device_id, app_version)
		event_id = request.GET["event_id"]
		try:
			event_obj = Event.objects.get(id=int(event_id))
		except:
			message = "Event is invalid"
			return error_response(message, return_data)
		event_comment_list = EventComments.objects.filter(event = event_obj)
		eventcomment = GetEventCommentsSerializer(event_comment_list,context={"request": request},many = True).data
		return_data = eventcomment
		message = "success"
		return success_response(message, return_data)

	def post(self,request):
		data = request.data
		serilazer = EventCommentsSerializer(data = data)
		serilazer.is_valid(raise_exception=True)
		platform = request.META.get('HTTP_PLATFORM', None)
		device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
		device_id = request.META.get('HTTP_DEVICE_ID', None)
		app_version = request.META.get('HTTP_APP_VERSION', None)
		validate_headers(platform, device_id, app_version)
		return_data = {}
		event_id = data["event_id"]
		message = data["message"]
		try:
			event_obj = Event.objects.get(id=int(event_id))
		except:
			message = "Event is invalid"
			return error_response(message, return_data)

		EventComments.objects.create(event = event_obj,sender=request.user,message = message)

		message = "success"
		return success_response(message, return_data)
