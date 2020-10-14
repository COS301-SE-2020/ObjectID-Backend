from datetime import datetime

from rest_framework import serializers
from .models import VehicleLog


class TrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleLog
        fields = '__all__'

class TrackingReturnSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    def get_date(self, obj):
        temp_date = obj.date

        return datetime.strftime(temp_date, "%Y-%M-%d - %H-%m")


    class Meta:
        model = VehicleLog
        fields = ('vehicle', 'date', 'lat', 'long', 'camera')