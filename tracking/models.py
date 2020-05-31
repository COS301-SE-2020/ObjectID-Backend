from django.db import models

from vehicle.models import Vehicle

# Create your models here.


class VehicleLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='tracking')
    date = models.DateTimeField()
    location = models.CharField(max_length=256) # TODO: Check if we make this set locations. I.e Gauteng as a key, then a city then etc etc
