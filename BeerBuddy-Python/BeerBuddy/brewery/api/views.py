
from users.api.permissions import IsAllowed
from rest_framework.views import APIView
from brewery.models import Brewery
from beershop.models import ConfigParam
from base.utils.utilities import (validate_headers,error_response,success_response,
                                  create_notification,send_notification, haversine)

from brewery.models import Offer
from django.utils import timezone
  
class NearByBreweryAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args,**kwargs):
        data = request.data
        # serializer = BeerCheckOutSerializer(data=data)
        if data:
            platform = request.META.get('HTTP_PLATFORM', None)
            device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
            device_id = request.META.get('HTTP_DEVICE_ID', None)
            app_version = request.META.get('HTTP_APP_VERSION', None)

            validate_headers(platform, device_id, app_version)
            return_data = {}
            result = []
            hit_google_api = True
            print(data)
            # beer_category = data["category"]
            lat1 = float(data['latitude'])
            lon1 = float(data['longitude'])
            user_obj = request.user
            beerplaces_obj = Brewery.objects.all()
            print(beerplaces_obj)
            if beerplaces_obj:
                try:
                    radius = float(ConfigParam.objects.all()[1].config['search_radius'])
                    print("radius", radius)
                except:
                    radius = 5.0
                min_distance = 0.0
                count = 0
                for beerplace in beerplaces_obj:
                    # call haversine formula
                    lat2, lon2 = float(beerplace.langitude), float(beerplace.longitude)
                    print(lat2, lon2,"brewery lat long")
                    distance = haversine(lat1, lon1, lat2, lon2)
                    print("DISTANCE-->", distance)
                    if distance < radius:
                        if count == 0:
                            print("if part")
                            min_distance = distance
                            # print(beerplace.placedata)
                            result.append(beerplace.placedata) 
                        if distance < min_distance:
                            print("second if part")
                            min_distance = distance
                            result.append(beerplace.placedata)
            else:
                pass
            if not return_data:
                hit_google_api = False
            print(result,"Result=========")
            return_data["status"] = "OK"
            return_data["results"] = result
            message = "success"
            return success_response(message, return_data)

class NearByOffersAPIView(APIView):
    permission_classes = [IsAllowed]

    def post(self, request, *args,**kwargs):
        try:
            data = request.data
            print(data, "offers")
            offer_data = []
            meta = request.META
            if data:
                platform = request.META.get('HTTP_PLATFORM', None)
                device_token = request.META.get('HTTP_DEVICE_TOKEN', None)
                device_id = request.META.get('HTTP_DEVICE_ID', None)
                app_version = request.META.get('HTTP_APP_VERSION', None)

                validate_headers(platform, device_id, app_version)
                user_id = Brewery.objects.get(place_id = data["place_id"])
                print(user_id, "near by offers")
                offer_obj = Offer.objects.filter(user_id = user_id, expired=False, live=True)
                print(offer_obj)

                for i in offer_obj:
                    obj = {}
                    end_date = i.end_date.strftime('%d %B %Y')
                    print("END date ", end_date)
                    a = i.end_date > timezone.now()
                    print(a)
                    if a == True:
                        obj["id"] = i.id
                        obj["image"] = request.build_absolute_uri(i.offer_image.url)
                        print(obj["image"],"IMAGE")
                        obj["title"] = i.offer_title
                        obj["description"] = i.offer_desc
                        obj["validTill"] = end_date
                        
                        offer_data.append(obj)
                print(offer_data)
                return success_response("success", offer_data)
        except Exception as e:
            print(e,"nearby offers")
            return error_response("error", {"error" : str(e)})

