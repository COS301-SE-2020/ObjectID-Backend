from django.shortcuts import render
from tools.viewsets import ActionAPI, validate_params



class DashBoardBase(ActionAPI):
    """
    The base class for all endpoints dashboard and statics related
    """

    