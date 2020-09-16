from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vehicle, ImageSpacec
from darknet_dmg import detect

@receiver(post_save, sender=Vehicle)
def damage_detection(sender, instance, **kwargs):
    image = ImageSpace.objects.filter(vehicle=instance.id).last()
    path = image.image.path
    output = detect.detect(path)
    print(output)
    #./darknet detector test data/obj.data cfg/yolov4-obj.cfg /mydrive/yolov4/backup/yolov4-obj_3000.weights /mydrive/images/car2.jpg -thresh 0.3

