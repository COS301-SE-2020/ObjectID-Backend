from django.shortcuts import render

from rest_framework import permissions

from .models import Vehicle
from .serializers import VehicleSerializer
from tools.viewsets import ActionAPI, validate_params


class VehicleBase(ActionAPI):

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['license_plate'])
    def get_vehicle(self, request, params=None, *args, **kwargs):
        """
        Simply a way of getting all the information on a specified vehicle
        """
        try:
            vehicle = Vehicle.objects.get(license_plate=params['license_plate'])
        except Vehicle.DoesNotExist:
            return {
                "success": False,
                "message": "Vehicle with that license plate does not exist"
            }

        serializer = VehicleSerializer(vehicle)
        return serializer.data
        

    @validate_params(['license_plate', 'color', 'make', 'model'])
    def add_vehicle_basic(self, request, params=None, *args, **kwargs):
        """
        Used to add vehicles
        """

        # TODO: Implement SAPS flag checking

        # TODO: Implement sending warnings on duplicates

        vehicle = Vehicle.objects.filter(license_plate=params['license_plate'])

        if vehicle.count() > 0:
            vehicle = vehicle[0]

            if params['make'] != vehicle.make or vehicle.model != params['model'] or vehicle.color != params['color']:
                # This license plate is a duplicate in this case
                vehicle.license_plate_duplicate = True
                vehicle.save()
                data = {
                    "license_plate": params["license_plate"],
                    "make": params["make"],
                    "model": params["model"],
                    "color": params["color"],
                    "saps_flagged": False,
                    "license_plate_duplicate": True
                }

                serializer = VehicleSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return serializer.data
                return serializer.errors

            # This vehicle is not a duplicate but already exists within the system
            # TODO: Add tracking stuff
        
        # This vehicle is not within our system yet, add it

        data = {
            "license_plate": params["license_plate"],
            "make": params["make"],
            "model": params["model"],
            "color": params["color"],
            "saps_flagged": False, #TODO: Add this checking stuff
            "license_plate_duplicate": False
        }

        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        data = {
            "success": False,
            "payload": serializer.errors
        }
        return data
