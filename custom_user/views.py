from django.shortcuts import render
from django.core.mail import send_mail

from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params
from .forms import RegisterForm
from email_custom.utils import send

class CustomUserBase(ActionAPI):

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['email', 'password1', 'username', 'password2'])
    def register_user(self, request, params=None, *args, **kwargs):
        form = RegisterForm(params)

        if form.is_valid():
            form.save()

            # send_mail(
            #     'ObjectID Registration',
            #     'Your email address was successfully registered with ObjectID',
            #     'ctrl.intelligence@gmail.com',
            #     [params["email"]],
            #     fail_silently=False
            # )
            #send(params['email'], 1)

            return {"success": True}
        else:
            return {
                "success": False,
                "payload": form.errors
            }