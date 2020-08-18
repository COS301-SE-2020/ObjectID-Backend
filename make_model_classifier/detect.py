from openalpr import Alpr
import sys
import os
import json
import subprocess


def detect_make_model(path):
    # cmd = "alpr -c eu -j {}".format(path)
    # result = os.system(cmd)
    result = subprocess.run(['python','make_model_classifier/car_make_model_classifier_yolo3.py','--image',path], stdout=subprocess.PIPE)
    return result.stdout

# return result.stdout
