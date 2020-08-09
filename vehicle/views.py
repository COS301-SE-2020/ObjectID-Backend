from datetime import datetime

from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from rest_framework import permissions, filters

from .models import Vehicle, ImageSpace, MarkedVehicle
from .serializers import VehicleSerializer, MarkedVehicleSerializer
from .utils import check_for_mark, open_cam_rtsp
from tracking.serializers import TrackingSerializer
from tools.viewsets import ActionAPI, validate_params

import cv2
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import requests
import numpy as np
from openalpr import Alpr
import sys


class VehicleBase(ActionAPI):
    
    permission_classes = [permissions.IsAuthenticated, ] 
    @csrf_exempt
    @validate_params(['vehicle_id'])
    def get_vehicle(self, request, params=None, *args, **kwargs):
        """
        Simply a way of getting all the information on a specified vehicle
        """
        try:
            vehicle = Vehicle.objects.get(pk=params['vehicle_id'])
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
        check_for_mark(params['license_plate'])

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
                        "vehicle": serializer.data.get("id"),
                        "date": datetime.now(),
                        "lat": params.get("lat", None),
                        "long": params.get("long", None)
                    }
                    tracking_serializer = TrackingSerializer(data=tracking_data)
                    if tracking_serializer.is_valid():
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
            if (tracking_serializer.is_valid()):
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
                "vehicle": serializer.data.get("id"),
                "date": datetime.now(),
                "lat": params.get("lat", None),
                "long": params.get("long", None)
            }
            tracking_serializer = TrackingSerializer(data=tracking_data)
            if tracking_serializer.is_valid():
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
        check_for_mark(params['license_plate'])

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
                        "lat": params.get("lat", None),
                        "long": params.get("long", None)
                    }
                    tracking_serializer = TrackingSerializer(data=tracking_data)
                    tracking_serializer.save()

                    image.vehicle = serializer.validated_data
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
            if tracking_serializer.is_valid():
                tracking_serializer.save()
            image.vehicle = vehicle
            image.save()

            # TODO: Implement image ID and damage saving

            return {
                "success": True,
                "message": "Vehicle tracked"
            }
        
        # This vehicle is not within our system yet, add it

        url = "https://engine.metagrated.com/api/v3/lookup"
        license_plate = params["license_plate"]
        license_plate = str(license_plate)
        payload = "{\r\n\t\"camera_id\":837,\r\n\t\"number_plate\":"+"\""+license_plate+"\""+",\r\n\t\"latitude\":\"0\",\r\n\t\"longitude\":\"0\"\r\n}\r\n"
        
        headers = {
  'Content-Type': 'application/json',
  'x-api-key': '973c5229fb362f63db25b3131b45b17a119d05cb',
  'Accept': 'application/json'
}

        response = requests.request("POST", url, headers=headers, data = payload)
        sapsFlagged = False
        if '\"Y\"' in response.text.encode('utf8'):
            sapsFlagged = True


        data = {
            "license_plate": params["license_plate"],
            "make": params["make"],
            "model": params["model"],
            "color": params["color"],
            "saps_flagged": sapsFlagged, #Saps stuff done
            "license_plate_duplicate": False
        }

        serializer = VehicleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            tracking_data = {
                "vehicle": serializer.data.get("id"),
                "date": datetime.now(),
                "lat": params.get("lat", None),
                "long": params.get("long", None)
            }
            tracking_serializer = TrackingSerializer(data=tracking_data)
            if tracking_serializer.is_valid():
                tracking_serializer.save()

            image.vehicle = serializer.validated_data
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

      
    @csrf_exempt
    def detect(self, request, params=None, *args, **kwags):
        os.environ['DISPLAY'] = ':0'

        data = request.FILES['file'] # or self.files['image'] in your form

        path = default_storage.save('vehicle/training_data/video.avi', ContentFile(data.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        
        # capture frames from a video
        cap = cv2.VideoCapture(tmp_file)

        # Trained XML classifiers describes some features of some object we want to detect
        car_cascade = cv2.CascadeClassifier('vehicle/training_data/cars.xml')

        # loop runs if capturing has been initialized.
        while True:
            # reads frames from a video
            ret, frames = cap.read()
                # convert to gray scale of each frames
            gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
            # Detects cars of different sizes in the input image
            cars = car_cascade.detectMultiScale(gray, 1.1, 1)
            # To draw a rectangle in each cars
            for (x,y,w,h) in cars:
                cv2.rectangle(frames,(x,y),(x+w,y+h),(0,0,255),2)
        # Display frames in a window 
                cv2.imshow('video', frames)
            # Wait for Esc key to stop
            if cv2.waitKey(33) == 27:
                break
        # De-allocate any associated memory usage
        cv2.destroyAllWindows()

        return {"success" : True}

    @validate_params(['license_plate'])
    def add_marked_vehicle(self, request, params=None, *args, **kwargs):
        """
        Used to add a marked vehicle
        """

        data = {
            "license_plate": params['license_plate'],
            "marked_by": request.user.id
        }


        serializer = MarkedVehicleSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return {
                "success": True
            }

        return {
            "success": False,
            "payload": serializer.errors
        }

    def get_marked_vehicles(self, request, params=None, *args, **kwargs):
        """
        Used to retrieve a dataset of the marked vehicles by the current auth'd user
        """

        queryset = MarkedVehicle.objects.filter(marked_by=request.user)

        if queryset.count() > 0:
            serializer = MarkedVehicleSerializer(queryset, many=True)
            return serializer.data
        
        return {
            "message": "There are no vehicles marked by this user"
        }

    @validate_params(['license_plate'])
    def remove_marked_vehicle(self, request, params=None, *args, **kwargs):
        """
        Used to remove a marked vehicle
        """

        queryset = MarkedVehicle.objects.filter(license_plate=params['license_plate'])

        if queryset.count() > 0:
            queryset.delete()
            return {
                "success": True
            }

        return {
            "success": False,
            "message": "There are no vehicles marked with that license plate"
        }


    @csrf_exempt
    @validate_params(['vehicle_id'])
    def edit_vehicle(self, request, params=None, *args, **kwargs):
        """
        Used to edit and existing vehicles attributes
        """

        try:
            vehicle = Vehicle.objects.get(pk=params['vehicle_id'])
        except Vehicle.DoesNotExist:
            return {
                "success": False,
                "message": "Vehicle with that license plate does not exist"
            }  

        if (params.get("license_plate_duplicate", None) in [False, 'false', 'False']) and (vehicle.license_plate_duplicate is True) and (params.get("license_plate", None)):
            qs = Vehicle.objects.filter(license_plate=vehicle.license_plate).exclude(id=vehicle.id)
            if qs.count() < 2:
                qs = qs[0]
                qs.license_plate_duplicate = False
                qs.save()
        
        if (params.get("license_plate_duplicate", None) in [True, 'true', 'True']) and (vehicle.license_plate_duplicate is False) and (params.get("license_plate", None)):
            qs = Vehicle.objects.filter(license_plate = params.get("license_plate"))
            for item in qs:
                item.license_plate_duplicate = True
                item.save()

        vehicle.license_plate = params.get("license_plate", vehicle.license_plate)
        vehicle.make = params.get('make', vehicle.make)
        vehicle.model = params.get('model', vehicle.model)
        vehicle.color = params.get('color', vehicle.color)
        vehicle.saps_flagged = params.get('saps_flagged', vehicle.saps_flagged)
        flag = params.get('license_plate_duplicate', vehicle.license_plate_duplicate)
        if flag in [False, 'false', 'False']:
            flag = False
        if flag in [True, 'true', 'True']:
            flag = True
        vehicle.license_plate_duplicate = flag

        vehicle.save()
        serializer = VehicleSerializer(vehicle)

        return serializer.data

    @validate_params(["camera_url", "camera_location"])
    def stream_analyzer(self, request, params=None, *args, **kwargs):

        camera_url = params["camera_url"]
        camera_url = params["camera_location"]

        alpr = Alpr('eu', 'eu.conf', '/usr/share/openalpr/runtime_data')  
        if not alpr.is_loaded():
            return{"success" : False,
                "Error" : 'Error loading OpenALPR'}
        alpr.set_top_n(3)

        cap = open_cam_rtsp(camera_url) #CALL FOR CAMERA STREAMS
        if not cap.isOpened():
            alpr.unload()
            return {"success" : False,
                "Error" : "Failed to open video file!"}
        cv2.namedWindow("OpenALPR", cv2.WINDOW_AUTOSIZE)
        cv2.setWindowTitle("OpenALPR", 'OpenALPR video test')

        _frame_number = 0
        while True:
            ret_val, frame = cap.read()
            if not ret_val:
                return {"success" : False,
                "Error" : 'VidepCapture.read() failed'}

            _frame_number += 1
            if _frame_number % 15 != 0:
                continue
            cv2.imshow("OpenALPR", frame)

            results = alpr.recognize_ndarray(frame)
            for i, plate in enumerate(results['results']):
                best_candidate = plate['candidates'][0]
                res = 'Plate #{}: {:7s} ({:.2f}%)'.format(i, best_candidate['plate'].upper(), best_candidate['confidence'])
                return {"success" : True,
                        "payload" : res}

            if cv2.waitKey(1) == 27:
                break

        cv2.destroyAllWindows()
        cap.release()
        alpr.unload()

    def test(self, request, params=None, *args, **kwargs):
        url = "https://engine.metagrated.com/api/v3/lookup"
        license_plate = params["license_plate"]
        license_plate = str(license_plate)
        payload = "{\r\n\t\"camera_id\":837,\r\n\t\"number_plate\":"+"\""+license_plate+"\""+",\r\n\t\"latitude\":\"0\",\r\n\t\"longitude\":\"0\"\r\n}\r\n"
        
        headers = {
  'Content-Type': 'application/json',
  'x-api-key': '973c5229fb362f63db25b3131b45b17a119d05cb',
  'Accept': 'application/json'
}

        response = requests.request("POST", url, headers=headers, data = payload)
        sapsFlagged = False
        if '\"N\"' in response.text:
            sapsFlagged = True
        return {"success" : sapsFlagged}

   
