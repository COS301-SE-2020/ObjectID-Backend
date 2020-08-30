from django.db import models

from django.contrib.auth import get_user_model


class Business(models.Model):
    related_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='business')
    name = models.CharField(max_length=64)
    logo = models.ImageField(upload_to='business/logos/')

    def __str__(self):
        return self.name