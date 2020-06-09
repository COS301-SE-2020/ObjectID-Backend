from django.conf.urls import include, url
from django.urls import path, re_path

urlpatterns = [
    re_path(r'v1/', include('rest_api.urls_v1')),
]