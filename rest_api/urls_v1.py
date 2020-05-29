from django.conf.urls import url

import vehicle.views as vehicle_viewset

urlpatterns = [
    url(r'vehicle/(P<action>[^/.]+)', vehicle_viewset.VehicleBase.as_view(), name='vehicle'),
]