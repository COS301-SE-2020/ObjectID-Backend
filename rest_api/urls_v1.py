from django.conf.urls import url, include
from django.urls import path, re_path

import vehicle.views as vehicle_viewset
import custom_user.views as custom_user_viewset
import camera.views as camera_viewset
import dashboard.views as dashboard_viewset

urlpatterns = [
    re_path(r'vehicle/(?P<action>[^/.]+)', vehicle_viewset.VehicleBase.as_view(), name='vehicle'),
    re_path(r'user/(?P<action>[^/.]+)', custom_user_viewset.CustomUserBase.as_view(), name='custom_user'),
    re_path(r'business/(?P<action>[^/.]+)', custom_user_viewset.BusinessBase.as_view(), name='business'),
    re_path(r'camera/(?P<action>[^/.]+)', camera_viewset.CameraActions.as_view(), name='camera'),
    re_path(r'dashboard/(?P<action>[^/.]+)', dashboard_viewset.DashBoardBase.as_view(), name='dashboard'),
    url(r'^password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]