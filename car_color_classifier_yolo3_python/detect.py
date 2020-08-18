from openalpr import Alpr
import sys
import os
import json
import subprocess


def detect(path):
    # cmd = "alpr -c eu -j {}".format(path)
    # result = os.system(cmd)
    result = subprocess.run(['python','car_color_classifier_yolo3_python/car_color_classifier_yolo3.py','--image',path], stdout=subprocess.PIPE)
    return result.stdout

# return result.stdout
