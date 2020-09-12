import email_to
from .secrets import email_password

from vehicle.models import Vehicle
from vehicle.models import MarkedVehicle


class EmailEngine():

    def __init__(self):
        self.server = email_to.EmailServer(
            'smtp.gmail.com',
            587,
            'ctrl.intelligence@gmail.com',
            email_password
        )

    def send_registration_email(self, address=None):
        """
        Sends an email to specified address to confirm registration
        """

        if not address:
            return False

        subject = "Object ID Successful Registration"
        message = "Welcome\n You have been registered on the ObjectID system. You will now have access to the system features."

        self.server.quick_email(address, subject, message)
        return True


    def send_deregistration_email(self, address=None):
        """
        Send notification email to notify of account removal
        """

        if not address:
            return False

        subject = "Your ObjectID account has been removed"
        message = "Your account has been removed from ObjectID. You will no longer have access to the system"

        self.server.quick_email(address, subject, message)
        return True

    def send_flagged_notification(self, address=None, vehicle=None):
        """
        Send an email for a flagged vehicle
        """

        if not address or not vehicle:
            return False

        log = Vehicle.tracking.last("id")
        mark = MarkedVehicle.objects.get(license_plate__iexact=vehicle.license_plate)

        subject = "ObjectID: Flagged Vehicle Spotted"
        message = "A vehicle that you have marked for reason: {}\n Has been spotted at\nLat:{} \nLong{}\n"\
            "Vehicle:{}\n Color:{} \n Make:{}\nModel:{}\n".format(
                mark.reason, log.camera.lat, log.camera.long,
                vehicle.license_plate, vehicle.color, vehicle.make, vehicle.model
            )

        self.server.quick_email(address, subject, message)
        return True

    def send_saps_flag_notification(self, address, vehicle):
        """
        Send an email to notify of saps flagged vehicle spotted
        """

        if not address or not vehicle:
            return False

        log = Vehicle.tracking.last("id")

        subject = "ObjectID: SAPS Flagged Vehicle Spotted"
        message = "A vehicle that has been flagged by saps as either stolen or involved in crime has been spotted.\n"\
            "Location:\nLat:{}\nLong:{}\nCamera Name:{}\n"\
                "License Plate:{}".format(
                    log.camera.lat, log.camera.long, log.camera.name,
                    vehicle.license_plate
                )

        self.server.quick_email(address, subject, message)
        return True