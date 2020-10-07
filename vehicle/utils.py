from .models import MarkedVehicle, Accuracy
from tracking.models import VehicleLog
from .serializers import AccuracySerializer
from django.core.mail import send_mail
import requests


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

def saps_API(params=None, *args, **kwargs):
        url = "https://engine.metagrated.com/api/v3/lookup"
        license_plate = params["license_plate"]
        license_plate = str(license_plate)
        payload = "{\r\n\t\"camera_id\":837,\r\n\t\"number_plate\":"+"\""+license_plate+"\""+",\r\n\t\"latitude\":\"0\",\r\n\t\"longitude\":\"0\"\r\n}\r\n"
        
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': '973c5229fb362f63db25b3131b45b17a119d05cb',
        'Accept': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data = payload)
        sapsFlagged = False
        if '\"Y\"' in response.text:
            sapsFlagged = True
        return sapsFlagged

def colour_detection(path):

    from car_color_classifier_yolo3_python.detect import detect
    color = detect(path)
    return color

def make_model_detection(path):
    from make_model_classifier.detect import detect_make_model
    make_model = detect_make_model(path)
    return make_model

def damage_detection(vehicle):
    from darknet_dmg import detect
    frontPerc = 0
    sidePerc = 0
    rearPerc = 0
    res = []
    image = vehicle.images.all().last()
    path = image.image.path
    output = detect.detect(path)
    output = output.decode("utf-8")
    side = output.find("side: ")
    rear = output.find("rear: ")
    front = output.find("front: ")
    if front != -1:
        res.append("Front")
        frontPerc = output[(front+7):(front+9)]

    if side != -1:
        res.append("Side")
        sidePerc = output[(front+6):(front+8)]
    if rear != -1:
        res.append("Rear")
        rearPerc = output[(front+6):(front+8)]
    perc = "0"

    if rearPerc > sidePerc:
        perc = rearPerc
    else:
        perc = sidePerc

    if perc > frontPerc:
        perc = perc
    else:
        perc = frontPerc

    from decimal import Decimal
    perc = [Decimal(perc.strip(' "'))]

    acc = Accuracy.objects.get(vehicle__id=vehicle.id)
    acc.damage_accuracy = perc 
    acc.save()
 
    return res
    #./darknet detector test data/obj.data cfg/yolov4-obj.cfg /mydrive/yolov4/backup/yolov4-obj_3000.weights /mydrive/images/car2.jpg -thresh 0.3
        