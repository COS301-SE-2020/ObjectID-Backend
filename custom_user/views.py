import uuid

from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params
from .forms import RegisterForm
from .models import Business
from custom_user.send_email import send
from camera.models import Camera

from camera.serializers import (
    CameraReturnSerializer,
    CameraSerializer
)

from custom_user import send_email
from email_engine import EmailEngine

class CustomUserBase(ActionAPI):

    permission_classes = [permissions.AllowAny, ]

    @validate_params(['email', 'password1', 'username', 'password2'])
    def register_user(self, request, params=None, *args, **kwargs):


        user_duplicate_check = get_user_model().objects.filter(email=params["email"])
        if user_duplicate_check.count() > 0:
            return {
                "success": False,
                "message": "A user with that email already exists"
            }

        form = RegisterForm(params)

        if form.is_valid():
            form.save()
            # send(params['email'], 1)

            # Create a blank business profile for that same user which will now be the
            # Owner of the business and the only user related to that business

            user_model = get_user_model()
            user = user_model.objects.get(email=params['email'])

            Business.objects.create(related_user=user, name="Replace This")

            # Create a single camera instance that will be used as the default when manually
            # Uploading images

            special_id = uuid.uuid4()

            # Make sure there are no other cameras with the same unique_key
            qs = Camera.objects.filter(unique_key=special_id)

            while qs.count() > 0:
                special_id = uuid.uuid4()
                qs = Camera.objects.filter(unique_key=special_id)

            Camera.objects.create(
                owner=user,
                lat=0,
                long=0,
                unique_key=special_id,
                name="Manual"
            )

            email_engine = EmailEngine()

            try:
                email_engine.send_registration_email(params["email"])
                return {
                    "success": True,
                    "message": "Confirmation email sent"
                }
            except Exception as e:
                return {
                    "success": True,
                    "payload": {
                        "error": "User successfully registered but there was an error sending the confirmation email"
                    }
                }
            return {"success": True}
        else:
            return {
                "success": False,
                "payload": form.errors
            }

class BusinessBase(ActionAPI):

    permission_classes = [permissions.IsAuthenticated, ]


    @validate_params(['name'])
    def edit_business_name(self, request, params=None, *args, **kwargs):
        """
        Used to modify the name of the business
        """
        business = Business.objects.get(related_user=request.user)
        business.name = params["name"]
        business.save()

        return {
            "success": True
        }

    @validate_params(['file'])
    def add_logo(self, request, params=None, *args, **kwargs):
        """
        Used to add or change the logo that the business has
        """

        business = Business.objects.get(related_user=request.user)
        business.logo = params['file']
        business.save()
        return {
            "success": True
        }

    def get_logo(self, request, params=None, *args, **kwargs):
        """
        Used to get the logo of the business
        """

        business = Business.objects.get(related_user=request.user)
        path = business.logo.path

        try:
            with open(path, 'rb') as f:
                return HttpResponse(f.read(), content_type="image/jpeg")
        except IOError:
            return {
                "success": False,
                "message": "No logo set for the business"
            }

    @validate_params(['name'])
    def add_camera(self, request, params=None, *args, **kwargs):
        """
        Used to add a camera that the business can use
        """

        # Make sure there are no other cameras with the same unique_key
        key = uuid.uuid4()
        test_qs = Camera.objects.filter(unique_key=key)

        while test_qs.count() > 0:
            key = uuid.uuid4()
            test_qs = Camera.objects.filter(unique_key=key)


        data = {
            "owner": request.user.id,
            "lat": params.get("lat", 0),
            "long": params.get("long", 0),
            "unique_key": key,
            "name": params.get("name", "None")
        }

        serializer = CameraSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return serializer.data

        return {
            "success": False,
            "payload": serializer.errors
        }

    def get_all_cameras(self, request, params=None, *args, **kwargs):
        """
        Returns all the cameras related to the business, less the manual upload one
        """

        camera_qs = Camera.objects.filter(owner=request.user)
        #Exclude the manual image upload camera
        camera_qs = camera_qs.exclude(name="Manual")

        if camera_qs.count() > 0:
            serializer = CameraSerializer(camera_qs, many=True)
            return serializer.data
        
        return {
            "success": False,
            "message": "This business account has no cameras"
        }

    @validate_params(['unique_key'])
    def edit_camera(self, request, params=None, *args, **kwargs):
        
        try:
            camera = Camera.objects.get(unique_key=params["unique_key"])
        except Camera.DoesNotExist:
            return {
                "success": False,
                "message": "A camera with that key does not exist"
            }

        camera.name = params.get("name", camera.name)
        camera.lat = params.get("lat", camera.lat)
        camera.long = params.get("long", camera.long)
        
        camera.save()

        serializer = CameraReturnSerializer(camera)

        return serializer.data