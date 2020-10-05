from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=10, blank=True, null=True)
    make = models.CharField(max_length=64, blank=True, null=True)
    model = models.CharField(max_length=64, blank=True, null=True)
    color = models.CharField(max_length=32, blank=True, null=True) # TODO: Consider making this a Foreign key for set values?
    saps_flagged = models.BooleanField(default=False, blank=True, null=True)
    license_plate_duplicate = models.BooleanField(default=False, blank=True, null=True)
    

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
    reason = models.TextField(default=None, blank=True, null=True)

class Accuracy(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='accuracy')
    make_accuracy = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, default=None)
    model_accuracy = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, default=None)
    color_accuracy = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, default=None)
    license_plate_accuracy = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, default=None)
    damage_accuracy = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, default=None)


    def __str__(self):
        return "Accuracies: {}".format(self.vehicle.license_plate)

class DamageModel(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='damage_detections')
    image = models.ImageField(upload_to='damage_detection/%Y/%m/%d/')