from rest_framework import serializers
from .models import VehicleLog


class TrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLog
        fields = '__all__'