from django.shortcuts import render

from rest_framework import permissions

from tools.viewsets import ActionAPI, validate_params
from .forms import RegisterForm


class CustomUserBase(ActionAPI):

    permission_classes = [permissions.IsAuthenticated, ]

    @validate_params(['email', 'password1', 'username', 'password2'])
    def register_user(self, request, params=None, *args, **kwargs):
        form = RegisterForm(params)

        if form.is_valid():
            form.save()
            return {"success": True}
        else:
            return {
                "success": False,
                "payload": form.errors
            }