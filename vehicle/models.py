from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10, blank=True)
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    color = models.CharField(max_length=32) # TODO: Consider making this a Foreign key for set values?
    saps_flagged = models.BooleanField(default=False)
    license_plate_duplicate = models.BooleanField(default=False)
    

    def __str__(self):
        return "{}: {} {}".format(self.model, self.license_plate, self.color)


class DamageType(models.Model):
    description = models.CharField(max_length=128)

    def __str__(self):
        return self.description

class Damage(models.Model):
    FRONT = "FRONT"
    REAR = "REAR"
    SIDE = "SIDE"
    location_choices = [
        (FRONT, "Front"),
        (REAR, "Rear"),
        (SIDE, "Side"),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='damage')
    location = models.CharField(max_length=128, choices=location_choices, default=None, null=True, blank=True)
    type = models.ForeignKey(DamageType, on_delete=models.CASCADE, related_name='damage', null=True, blank=True)
    image = models.ImageField(upload_to='damage_vehicle/%Y/%m/%d/', null=True, blank=True, default=None)

    def __str__(self):
        return "{}: at {}".format(self.vehicle.license_plate, self.location)

class ImageSpace(models.Model):
    image = models.ImageField(upload_to='vehicles/%Y/%m/%d/')
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.CASCADE, related_name="images")

class MarkedVehicle(models.Model):
    license_plate = models.CharField(max_length=10)
    marked_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='marked_vehicle')