
from rest_framework import serializers
from camera.models import Camera


class CameraTotalTrackSerializer(serializers.ModelSerializer):

    total = serializers.SerializerMethodField()
    total_saps_reads = serializers.SerializerMethodField()

    def get_total(self, obj):
        try:
            tracks = obj.tracking.all()
            return tracks.count()
        except:
            return 0

    def get_total_saps_reads(self, obj):
        try:
            tracks = obj.tracking.all()
            tracks = tracks.filter(vehicle__saps_flagged=True)
            return tracks.count()
        except:
            return 0

    class Meta:
        model = Camera
        fields = '__all__'