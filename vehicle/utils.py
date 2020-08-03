from .models import MarkedVehicle
from tracking.models import VehicleLog

from django.core.mail import send_mail


def check_for_mark(license_plate):

    queryset = MarkedVehicle.objects.filter(license_plate=license_plate)
    emails = []
    if queryset.count() > 0:
        for item in queryset:
            emails.append(item.marked_by.email)

        tracking_obj = VehicleLog.objects.filter(license_plate=license_plate).latest("id")
        send_mail(
            'ObjectID Vehicle Spotted',
            'The vehicle {} was spotted at Lat: {} Long: {}'.format(license_plate, tracking_obj.lat, tracking_obj.long),
            'ctrl.intelligence@gmail.com',
            emails,
            fail_silently=False
        )