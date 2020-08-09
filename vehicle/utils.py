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

def open_cam_rtsp(uri, width=1280, height=720, latency=2000): #code for adding a camera stream MUST BE RELOCATED
    gst_str = ('rtspsrc location={} latency={} ! '
               'rtph264depay ! h264parse ! omxh264dec ! nvvidconv ! '
               'video/x-raw, width=(int){}, height=(int){}, format=(string)BGRx ! '
               'videoconvert ! appsink').format(uri, latency, width, height)
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)