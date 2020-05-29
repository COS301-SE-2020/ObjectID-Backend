from django.conf.urls import include, url

urlpatterns = [
    url(r'^v1/', include('rest_api.urls_v1')),
]