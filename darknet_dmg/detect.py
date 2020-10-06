import sys
import os
import json
import subprocess


def detect(path):
    # cmd = "alpr -c eu -j {}".format(path)
    # result = os.system(cmd)
    result = subprocess.run(['./darknet_dmg/darknet','detector','test','darknet_dmg/data/obj.data','darknet_dmg/cfg/yolov4-obj.cfg','darknet_dmg/yolov4-obj_3000.weights',path,'-thresh 0.7', '-dont_show'], stdout=subprocess.PIPE)
    return result.stdout
    #./darknet detector test data/obj.data cfg/yolov4-obj.cfg darknet_dmg/yolov4-obj_3000.weights darknet_dmg/predictions.jpg -thresh 0.3

# return result.stdout
