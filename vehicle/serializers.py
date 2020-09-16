from rest_framework import serializers
from .models import Vehicle, MarkedVehicle, Damage

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class MarkedVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarkedVehicle
        fields = '__all__'

class DamagedVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Damage
        fields = '__all__'