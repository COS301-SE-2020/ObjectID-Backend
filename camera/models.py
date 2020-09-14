from django.db import models
from django.contrib.auth import get_user_model

import uuid


class Camera(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='cameras')
    lat = models.DecimalField(blank=True, max_digits=9, decimal_places=6, default=None, null=True)
    long = models.DecimalField(blank=True, max_digits=9, decimal_places=6, default=None, null=True)
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)

    def __str__(self):
        return "Camera: {}".format(self.name)