import requests
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params
from .models import Camera
from vehicle.models import Vehicle, ImageSpace
from tracking.models import VehicleLog

from vehicle.utils import check_for_mark, saps_API

from vehicle.serializers import VehicleSerializer, MarkedVehicleSerializer
from tracking.serializers import TrackingSerializer

class CameraActions(ActionAPI):

    permission_classes = [permissions.AllowAny, ]

    @validate_params(["file", "key"])
    def add(self, request, params=None, *args, **kwargs):
        
        try:
            camera = Camera.objects.get(unique_key=params['key'])
        except Camera.DoesNotExist:
            return HttpResponse({
                "success": False,
                "message": "Invalid Key"
            }, status=401)

        image_space = ImageSpace(image=params["file"])
        image_space.save()

        path = image_space.image.path
        
        tracking = {
            "vehicle": None,
            "date": datetime.now(),
            "lat": camera.lat,
            "long": camera.long,
            "camera": camera
        }

        res = None

        # Check if we have been provided with the license plate of the vehicle
        # If not get it
        if not params.get("license_plate", None):

            regions = ['za'] # Change to your country
            with open(path, 'rb') as fp:
                response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                data=dict(regions=regions),  # Optional
                files=dict(upload=fp),
                headers={'Authorization': 'token 8e744c1226777aa96d25e06807b69cbfc03f4c72'})
            res = response.json()
            
            if res.get("error", None):
                return {
                    "success": False,
                    "message": "Invalid file"
                }

            res = res["results"]
        
        if len(res) > 0:
            special_plate = res[0]['plate']
        else:
            special_plate = ""

        data = {
            "license_plate": params.get("license_plate", special_plate),
            "color": params.get("color", None),
            "make": params.get("make", None),
            "model": params.get("model", None),
            "saps_flagged": False,
            "license_plate_duplicate": False
        }

        # If we have the plate check if it has been marked by anyone
        if data["license_plate"] is not None and data["license_plate"] != "":
            check_for_mark(data["license_plate"])
        
        # Do the color checking and fetching
        if not data["color"]:
            from vehicle.utils import colour_detection
            bytes_ret = colour_detection(path)
            data["color"] = bytes_ret.decode("utf-8")
        
        # Do the make and model checking and fetching
        if not data["make"]:
            from vehicle.utils import make_model_detection
            bytes_ret = make_model_detection(path)
            bytes_ret = bytes_ret.decode("utf-8").split(":")
            data["model"] = bytes_ret[0]
            data["make"] = bytes_ret[1]
        
        saps_flag = saps_API(params={"license_plate": data["license_plate"]}, *args, **kwargs)
        data["saps_flagged"] = saps_flag

        # TODO: Check the logic below, what happens when there is a third vehicle with the same plate?

        # Start the checking if duplicate vehicles
        duplicate_check = Vehicle.objects.filter(license_plate__iexact=data["license_plate"])
        if duplicate_check.count() > 0:
            # We have a car with the same license plate in the system
            for duplicate_item in duplicate_check:
                # Go through each vehicle with the same license plate
                if duplicate_item.make.lower() == data["make"].lower() and\
                    duplicate_item.model.lower() == data["model"].lower() and\
                    duplicate_item.color.lower() == data["color"].lower():
                    # The vehicle was the same vehicle
                    tracking["vehicle"] = duplicate_item.id
                    tracking_serializer = TrackingSerializer(data=tracking)
                    if tracking_serializer.is_valid():
                        tracking_serializer.save()
                    image_space.vehicle = duplicate_item.id
                    image_space.save()
                    # Check the saps flagging
                    if saps_flag:
                        tracking_qs = VehicleLog.objects.filter(vehicle__id=duplicate_item.id).latest("id")
                        location = "Lat: {}, Long: {}".format(tracking_qs.lat, tracking_qs.long)
                        send_email.flagged_notification(
                            request.user.email,
                            duplicate_item.license_plate,
                            "This vehicle was involved in theft or possibly stolen",
                            params["file"], location, duplicate_item.make,
                            duplicate_item.model, duplicate_item.color
                        )
                    return {
                        "success": True
                    }
                else:
                    # The vehicle is a different vehicle
                    duplicate_item.license_plate_duplicate = True
                    duplicate_item.save()
                    data["license_plate_duplicate"] = True
                    serializer = VehicleSerializer(data=data)
                    if serializer.is_valid():
                        vehicle = serializer.save()
                        tracking["vehicle"] = vehicle.id
                        tracking_serializer = TrackingSerializer(data=tracking)
                        if tracking_serializer.is_valid():
                            tracking_serializer.save()
                        image_space.vehicle = vehicle
                        image_space.save()
                        if saps_flag:
                            tracking_qs = VehicleLog.objects.filter(vehicle__id=vehicle.id).latest("id")
                            location = "Lat: {}, Long: {}".format(tracking_qs.lat, tracking_qs.long)
                            send_email.flagged_notification(
                                request.user.email,
                                vehicle.license_plate,
                                "This vehicle was involved in theft or possibly stolen",
                                params["file"], location, vehicle.make,
                                vehicle.model, vehicle.color
                            )
                        return {
                            "success": True
                        }
        else:
            # We do not have the license plate in the database
            serializer = VehicleSerializer(data=data)
            if serializer.is_valid():
                vehicle = serializer.save()
                tracking["vehicle"] = vehicle.id
                tracking_serializer = TrackingSerializer(data=tracking)
                if tracking_serializer.is_valid():
                    tracking_serializer.save()
                image_space.vehicle = vehicle
                image_space.save()
                if saps_flag:
                    tracking_qs = VehicleLog.objects.filter(vehicle__id=vehicle.id).latest("id")
                    location = "Lat: {}, Long: {}".format(tracking_qs.lat, tracking_qs.long)
                    send_email.flagged_notification(
                        request.user.email,
                        vehicle.license_plate,
                        "This vehicle was involved in theft or possibly stolen",
                        params["file"], location, vehicle.make,
                        vehicle.model, vehicle.color
                    )
                return {
                    "success": True
                }

