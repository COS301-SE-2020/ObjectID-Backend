from openalpr import Alpr
import sys
import os
import json
import subprocess


def check_image(path):
    # cmd = "alpr -c eu -j {}".format(path)
    # result = os.system(cmd)
    result = subprocess.run(['alpr','-c','eu','-j',path], stdout=subprocess.PIPE)

    return json.loads(result.stdout)
