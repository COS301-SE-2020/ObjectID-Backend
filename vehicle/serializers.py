from rest_framework import serializers
from .models import Vehicle, MarkedVehicle, Damage, Accuracy

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

class AccuracySerializer(serializers.ModelSerializer):
    class Meta:
        model = Accuracy
        fields = '__all__'