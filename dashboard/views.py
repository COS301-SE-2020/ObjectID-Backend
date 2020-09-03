from django.shortcuts import render
from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params

from camera.models import Camera
from tracking.models import VehicleLog

from .serializers import CameraTotalTrackSerializer


class DashBoardBase(ActionAPI):
    """
    The base class for all endpoints dashboard and statics related
    """

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['unique_key'])
    def get_single_camera_total(self, request, params=None, *args, **kwargs):
        """
        Used to get the total number of read a single cameras has made
        """

        try:
            camera = Camera.objects.(unique_key=params['unique_key'])
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
