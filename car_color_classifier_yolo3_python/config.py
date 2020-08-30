# Copyright © 2019 by Spectrico
# Licensed under the MIT License
pre_path = "car_color_classifier_yolo3_python/"

model_file = "{}model-weights-spectrico-car-colors-mobilenet-224x224-052EAC82.pb".format(pre_path)  # path to the car color classifier
label_file = "{}labels.txt".format(pre_path)   # path to the text file, containing list with the supported makes and models
input_layer = "input_1"
output_layer = "softmax/Softmax"
classifier_input_size = (224, 224) # input size of the classifier
