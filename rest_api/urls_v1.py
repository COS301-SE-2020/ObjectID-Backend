from django.conf.urls import url
from django.urls import path, re_path

import vehicle.views as vehicle_viewset
import custom_user.views as custom_user_viewset

urlpatterns = [
    re_path(r'vehicle/(?P<action>[^/.]+)', vehicle_viewset.VehicleBase.as_view(), name='vehicle'),
    re_path(r'user/(?P<action>[^/.]+)', custom_user_viewset.CustomUserBase.as_view(), name='custom_user')
]