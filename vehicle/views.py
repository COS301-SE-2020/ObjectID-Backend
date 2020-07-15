from datetime import datetime

from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework import permissions, filters

from .models import Vehicle, ImageSpace
from .serializers import VehicleSerializer
from tracking.serializers import TrackingSerializer
from tools.viewsets import ActionAPI, validate_params


class VehicleBase(ActionAPI):
    # TODO: Place this back in when login is added
    permission_classes = [permissions.IsAuthenticated, ] 
    @csrf_exempt
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
        
    @csrf_exempt
    @validate_params(['license_plate', 'color', 'make', 'model'])
    def add_vehicle_basic(self, request, params=None, *args, **kwargs):
        """
        Used to add vehicles
        """

        # TODO: Implement SAPS flag checking

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
                    tracking_data = {
                        "vehicle": serializer.instance(),
                        "date": datetime.now(),
                        "location": params.get("location", "No location")
                    }
                    tracking_serializer = TrackingSerializer(data=tracking_data)
                    tracking_serializer.save()
                    return {
                        "success": True,
                        "duplicate": True,
                        "payload": {
                            "vehicles": serializer.data
                        }
                    }
                return serializer.errors

            # This vehicle is not a duplicate but already exists within the system
            tracking_data = {
                "vehicle": vehicle,
                "date": datetime.now(),
                "location": params.get("location", "No Location")
            }

            tracking_serializer = TrackingSerializer(data=tracking_data)
            tracking_serializer.save()

            return {
                "success": True,
                "message": "Vehicle tracked"
            }
        
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

            tracking_data = {
                "vehicle": serializer.instance(),
                "date": datetime.now(),
                "location": params.get("location", "No location")
            }
            tracking_serializer = TrackingSerializer(data=tracking_data)
            tracking_serializer.save()

            return serializer.data
        data = {
            "success": False,
            "payload": serializer.errors
        }
        return data

    @csrf_exempt
    @validate_params(["filters", "type"])
    def search_advanced(self, request, params=None, *args, **kwargs):
        """ 
        Used to search for vehicles by various paramaters
        """

        search_type = params.get("type", None)
        filters_param = params.get('filters', None)

        if search_type == "and":
            """AND TYPE SEARCH"""
            queryset = Vehicle.objects.all()

            if filter is None:
                return {
                    "success": False,
                    "message": "Filters argument not provided"
                }

            license_plate = filters_param.get('license_plate', None)
            make = filters_param.get('make', None)
            model = filters_param.get('model', None)
            color = filters_param.get('color', None)
            saps_flagged = filters_param.get('saps_flagged', None)
            license_plate_duplicate = filters_param.get('license_plate_duplicate', None)

            if license_plate:
                queryset = queryset.filter(license_plate=license_plate)

            if make:
                queryset = queryset.filter(make=make)

            if model:
                queryset = queryset.filter(model=model)
            
            if color:
                queryset = queryset.filter(color=color)

            if saps_flagged:
                queryset = queryset.filter(saps_flagged=saps_flagged)

            if license_plate_duplicate:
                queryset = queryset.filter(license_plate_duplicate=license_plate_duplicate)

            if queryset.count() == 0:
                return {
                    "success": False,
                    "message": "No items match this query"
                }

            serializer = VehicleSerializer(queryset, many=True)

            return serializer.data

        elif search_type == "or":
            """OR TYPE SEARCH"""
            queryset = Vehicle.objects.none()

            license_plate = filters_param.get('license_plate', None)
            make = filters_param.get('make', None)
            model = filters_param.get('model', None)
            color = filters_param.get('color', None)
            saps_flagged = filters_param.get('saps_flagged', None)
            license_plate_duplicate = filters_param.get('license_plate_duplicate', None)

            if license_plate:
                queryset |= Vehicle.objects.filter(license_plate=license_plate)
            if make:
                queryset |= Vehicle.objects.filter(make=make)
            if model:
                queryset |= Vehicle.objects.filter(model=model)
            if color:
                queryset |= Vehicle.objects.filter(color=color)
            if saps_flagged:
                queryset |= Vehicle.objects.filter(saps_flagged=saps_flagged)
            if license_plate_duplicate:
                queryset |= Vehicle.objects.filter(license_plate_duplicate=license_plate_duplicate)

            if queryset.count() == 0:
                return {
                    "success": False,
                    "message": "No data matching query"
                }

            serializer = VehicleSerializer(queryset, many=True)

            return serializer.data

        return {
            "success": False,
            "message": "Search type is not supported"
        }
    
    @validate_params(['search'])
    def search(self, request, params=None, *args, **kwargs):
        """
        Used to search the database of Vehicles by keywords
        """

        # TODO: Consider implementing multiple words?

        word_match = params.get("search", None)

        if word_match is None:
            return {
                "success": False,
                "message": "No search words were passed through"
            }

        queryset = Vehicle.objects.filter(
            Q(license_plate__icontains=word_match) |
            Q(make__icontains=word_match) |
            Q(model__icontains=word_match) |
            Q(color__icontains=word_match)
        )

        if queryset.count() == 0:
            return {
                "success": False,
                "message": "No items matching given keywords"
            }

        serializer = VehicleSerializer(queryset, many=True)
        return serializer.data

    @csrf_exempt
    def file_recognize(self, request, params=None, *args, **kwargs):
        """
        Used to upload a file and run it through OpenALPR and save an instance of a vehicle to that image
        """

        from lpr.lpr import check_image

        temp = ImageSpace(image=params['file'])
        temp.save()
        path = temp.image.path

        result = check_image(path)

        result = result.get('results', [])
        result = result[0]
        plate = result.get('plate', None)

        if plate is not None:
            # TODO: Implement all the 'tbi' factors as well as damage
            data = {
                'license_plate': plate,
                'color': 'tbi',
                'make' : 'tbi',
                'model': 'tbi',
                'saps_flagged': False,
                'license_plate_duplicate': False,
            }

            serializer = VehicleSerializer(data=data)
            if serializer.is_valid():
                vehicle = serializer.save()
                temp.vehicle = vehicle
                temp.save()
                return serializer.data
            return {
                "success": False,
                "payload": serializer.errors
            }

        return {
            "success": False,
            "reason": "Something went wrong with OpenALPR"
        }
    
    @validate_params(["license_plate", "make", "model", "color", "file"])
    def camera_add_full(self, request, params=None, *args, **kwargs):
        """
        Used to add an image and full vehicle data from a camera into the system
        """

        vehicle = Vehicle.objects.filter(license_plate=params['license_plate'])
        image = ImageSpace(image=params['file'])
        image.save()

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
                    tracking_data = {
                        "vehicle": serializer.instance(),
                        "date": datetime.now(),
                        "location": params.get("location", "No location")
                    }
                    tracking_serializer = TrackingSerializer(data=tracking_data)
                    tracking_serializer.save()

                    image.vehicle = serializer.instance()
                    image.save()

                    # TODO: Implement image ID and damage saving

                    return {
                        "success": True,
                        "duplicate": True,
                        "payload": {
                            "vehicles": serializer.data
                        }
                    }
                return serializer.errors

            # This vehicle is not a duplicate but already exists within the system
            tracking_data = {
                "vehicle": vehicle,
                "date": datetime.now(),
                "location": params.get("location", "No Location")
            }

            tracking_serializer = TrackingSerializer(data=tracking_data)
            tracking_serializer.save()
            image.vehicle = vehicle
            image.save()

            # TODO: Implement image ID and damage saving

            return {
                "success": True,
                "message": "Vehicle tracked"
            }
        
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

            tracking_data = {
                "vehicle": serializer.instance(),
                "date": datetime.now(),
                "location": params.get("location", "No location")
            }
            tracking_serializer = TrackingSerializer(data=tracking_data)
            tracking_serializer.save()

            image.vehicle = serializer.instance()
            image.save()

            # TODO: Implement image ID and damage saving

            return serializer.data
        data = {
            "success": False,
            "payload": serializer.errors
        }
        return data
        

    def get_saps_flagged(self, request, params=None, *args, **kwargs):
        """
        Used to retrieve the set of vehicles that have been flagged by SAPS and saved in our system
        """

        queryset = Vehicle.objects.filter(saps_flagged=True)

        serializer = VehicleSerializer(queryset, many=True)

        return serializer.data


    def get_duplicates(self, request, params=None, *args, **kwags):
        """
        Used to retrieve the set of vehicles that are duplicates
        """

        queryset = Vehicle.objects.filter(license_plate_duplicate=True)

        serializer = VehicleSerializer(queryset, many=True)

        return serializer.data

        