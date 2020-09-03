from datetime import datetime, timedelta

from django.shortcuts import render
from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params

from camera.models import Camera
from camera.serializers import CameraReturnSerializer
from tracking.models import VehicleLog

from .serializers import CameraTotalTrackSerializer
from .utils import date_ranger


class DashBoardBase(ActionAPI):
    """
    The base class for all endpoints dashboard and statics related
    """

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['unique_key'])
    def get_single_camera_read_total(self, request, params=None, *args, **kwargs):
        """
        Used to get the total number of read a single cameras has made
        """

        try:
            camera = Camera.objects.get(unique_key=params['unique_key'])
        except Camera.DoesNotExist:
            return {
                "success": False,
                "message": "Camera with that unique key does not exist"
            }

        tracking_qs = camera.tracking.all()
        return tracking_qs.count()


    def get_all_camera_total(self, request, params=None, *args, **kwargs):
        """
        Used to get all the camera totals that are related to that user
        """

        user = request.user

        camera_qs = user.cameras.all()

        serializer = CameraTotalTrackSerializer(camera_qs, many=True)

        return serializer.data


    @validate_params(['unique_key'])
    def get_camera_history(self, request, params=None, *args, **kwargs):
        """
        Used to get a cameras total count per day from and specified dates
        The dates default to today and 2 weeks ago
        """

        # Start with checking that the camera exists

        try:
            camera = Camera.objects.get(unique_key=params['unique_key'])
        except Camera.DoesNotExist:
            return {
                "success": False,
                "message": "Camera does not exist"
            }

        # Collect the specified dates otherwise default to current day and 2 weeks prior

        start_string = params.get('start', None)
        end_string = params.get('end', None)
        
        if end_string:
            end = datetime.strptime(end_string, '%Y-%m-%d')
        else:
            end = datetime.now()

        if start_string:
            start = datetime.strptime(start_string, '%Y-%m-%d')
        else:
            start = end + timedelta(days=-14)

        # Collect the tracking items related to that camera
        tracking_qs = camera.tracking.all()

        # Filter the queryset to be within the date range
        tracking_qs = tracking_qs.filter(date__range=(start, end))

        # Create the return item and do the daily grouping

        return_dict = {}
        # Add the camera information to the return dict
        cam_serializer = CameraReturnSerializer(camera)
        return_dict["camera"] = cam_serializer.data

        # Create a temp array to hold the information of the date and count
        counter_array = []
        for date in date_ranger(start, end):
            temp_obj = {
                "date": datetime.strftime("%Y-%m-%d", date),
                "count": tracking_qs.filter(date=date).count()
            }
            counter_array.append(temp_obj)

        return_dict["data"] = counter_array

        return return_dict

    def get_user_overview(self, request, params=None, *args, **kwargs):
        """
        Used to get a general overview of the user
        """

        user = request.user

        cameras = user.cameras.all()

        return_dict = {}

        # Get the total number of cameras that the user has added
        # -1 to exlucde the manual camera item
        return_dict["camera_total"] = cameras.count() - 1

        # Get the total number of saps flagged reads the user has
        # NOTE: This may be wrong and would require going through each camera?
        return_dict["total_saps_reads"] = cameras.tracking.all().filter(vehicle__saps_flagged=True).count()

        # Get the number of vehicles that this user currently has marked
        return_dict["marked_count"] = user.marked_vehicle.all().count()

        # Get the total number of reads that this users cameras have made
        return_dict["total_reads"] = cameras.tracking.all().count()

        # Get the total number of manual uploads that this user has made
        cam = cameras.filter(name="Manual")
        cam = cam[0]
        return_dict["total_manual_uploads"] = cam.tracking.all().count()

        return return_dict