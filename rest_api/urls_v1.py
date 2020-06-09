from django.conf.urls import url
from django.urls import path, re_path

import vehicle.views as vehicle_viewset

urlpatterns = [
    re_path(r'vehicle/(?P<action>[^/.]+)', vehicle_viewset.VehicleBase.as_view(), name='vehicle'),
]