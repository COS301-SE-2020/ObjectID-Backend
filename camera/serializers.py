from rest_framework import serializers

from .models import Camera

class CameraReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ('lat', 'long', 'unique_key')

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'