import requests
from celery import shared_task
from celery.utils.log import get_task_logger

from tracking.models import VehicleLog
from vehicle.models import Vehicle, Accuracy
from vehicle.utils import check_for_mark


@shared_task
def vehicle_detection(vehicle, image_space):
    

    if not vehicle.license_plate:
        vehicle.license_plate = license_plate_detection(image_space)
    check_for_mark(vehicle.license_plate)


    if not vehicle.color:
        vehicle.color = color_detection(vehicle, image_space)

    if not vehicle.make or not vehicle.model:
        vehicle.make, vehicle.model = make_model_detection(vehicle, image_space)

    saps_check(vehicle)

# TODO: Accuracy model inside here somewhere

def license_plate_detection(image_space):

    res = []
    regions = ['za']
    path = image_space.image.path

    with open(path, 'rb') as fp:
        response = requests.post(
          'https://api.platerecognizer.com/v1/plate-reader/',
                data=dict(regions=regions),  # Optional
                files=dict(upload=fp),
                headers={'Authorization': 'token 8e744c1226777aa96d25e06807b69cbfc03f4c72'}
                )
        res = response.json()

        if res.get("error", None):
            return "error"

        res = res["results"]

    if len(res) > 0:
        return res[0]['plate']


def color_detection(vehicle, image_space):
    from vehicle.utils import colour_detection
    bytes_ret = color_detection(image_space.image.path)
    return bytes_ret.decode("utf-8")

def make_model_detection(vehicle, image_space):
    from vehicle.utils import make_model_detection
    bytes_ret = make_model_detection(image_space.image.path)
    bytes_ret = bytes_ret.decode("utf-8").split(":")
    return bytes_ret[1], bytes_ret[0]

def damage_detection(vehicle, image_space):
    # TODO: (STEVE) add this please

def saps_check(vehicle):
    from vehicle.utils import saps_API
    vehicle.saps_flagged = saps_API(
        params={
            "license_plate": vehicle.license_plate
        },
    )

def duplicate_check(vehicle):
    # TODO: Move the duplicate checking stuff inside here as well