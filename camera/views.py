import requests
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params
from .models import Camera
from .tasks import vehicle_detection
from vehicle.models import Vehicle, ImageSpace, Accuracy
from tracking.models import VehicleLog

from vehicle.utils import check_for_mark, saps_API

from vehicle.serializers import VehicleSerializer, MarkedVehicleSerializer
from tracking.serializers import TrackingSerializer

from custom_user import send_email

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

        # Create an empty vehicle object to be used later with celery
        data = {
            "license_plate": params.get("license_plate", None),
            "color": params.get("color", None),
            "make": params.get("make", None),
            "model": params.get("model", None),
            "saps_flagged": False,
            "license_plate_duplicate": False
        }
        temp_vehicle = Vehicle.objects.create(
            license_plate=data["license_plate"],
            color=data["color"],
            make=data["make"],
            model=data["model"],
        )

        path = image_space.image.path
        
        tracking = {
            "vehicle": temp_vehicle.id,
            "date": datetime.now(),
            "lat": camera.lat,
            "long": camera.long,
            "camera": camera.id
        }

        image_space.vehicle = temp_vehicle
        image_space.save()

        tracking_serializer = TrackingSerializer(data=tracking)
        if tracking_serializer.is_valid():
            track = tracking_serializer.save()
            Accuracy.objects.create(vehicle=temp_vehicle)
            vehicle_detection.delay(temp_vehicle, track)
            return True
        
        saps_flag = saps_API(params={"license_plate": data["license_plate"]}, *args, **kwargs)
        data["saps_flagged"] = saps_flag

        # TODO: Move this logic inside the tasks file

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

