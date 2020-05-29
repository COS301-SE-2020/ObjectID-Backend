from django.shortcuts import render

from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params


class VehicleBase(ActionAPI):

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['vehicle_id'])
    def get_vehicle(self, request, params=None, *args, **kwargs):
        """
        Simply a way of getting all the information on a specified vehicle
        """
        pass