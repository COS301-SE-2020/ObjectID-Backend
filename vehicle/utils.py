from .models import MarkedVehicle


def check_for_mark(license_plate):

    queryset = MarkedVehicle.objects.filter(license_plate=license_plate)

    if queryset.count() > 0:
        # TODO: Send email to user
        pass