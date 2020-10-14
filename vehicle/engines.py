import requests

from .models import Accuracy, Vehicle, Damage, MarkedVehicle
from .serializers import VehicleSerializer, AccuracySerializer
from tracking.serializers import TrackingSerializer
from .utils import colour_detection, make_model_detection, damage_detection, saps_API

from django.db.models import Q




class VehicleClassificationEngine():
    """
    Engine to classify vehicles and save them etc
    """

    vehicle = None
    image = None
    tracking_data = None
    saps_flagged = False
    license_plate_duplicate = False

    def __init__(self, vehicle, image, tracking_data, to_address=None):
        self.vehicle = vehicle
        self.image = image
        self.tracking_data = tracking_data
        self.to_address = to_address

    def classify_vehicle(self):

        if self.vehicle is None or self.image is None or self.tracking_data is None:
            return "Engine paramater not set"

        # Classify the vehicle
        # Start with color
        self.detected_color, self.color_accuracy = colour_detection(self.image.image.path)
        # Make and model
        self.detected_make_model, self.make_model_accuracy = make_model_detection(self.image.image.path)
        # Damage
        self.detected_damage_location, self.damage_accuracy = damage_detection(self.image.image.path)
        # License plate
        self.detected_plate = self.__get_plate_information()

        # Decode the detections
        color_bytes = self.detected_color.split("\n")
        middle = color_bytes[0].find(",")
        color_bytes[0] = color_bytes[0][0:middle]
        self.detected_color = color_bytes[0]

        make_model_bytes = self.detected_make_model.split("\n")[0].split(":")
        if make_model_bytes[0] == "":
            make_model_bytes[0] = "N/A"
            make_model_bytes.append("N/A")
        else:
            middle = make_model_bytes[1].find(",")
            make_model_bytes[1] = make_model_bytes[1][0:middle]
        self.detected_make = make_model_bytes[1]
        self.detected_model = make_model_bytes[0]

        # If the license plate is not detected just save the new vehicle
        # Otherwise do comparison checks to see if we have the same vehicle or save a new vehicle

        if self.detected_plate == 1:
            return self.__save_vehicle("")
        
        perfect_check = self.__check_for_perfect_match()
        if perfect_check is not False:
            return self.__track_vehicle(perfect_check.id)

        duplicate_qs = self.__check_for_duplication_plates(self.detected_plate)

        if duplicate_qs is False:
            return self.__save_vehicle(self.detected_plate)
        
        for vehicle in duplicate_qs:
            vehicle.license_plate_duplicate = True
            vehicle.save()
        self.license_plate_duplicate = True
        return self.__save_vehicle(self.detected_plate)

    
    def __track_vehicle(self, vehicle_id):
        from email_engine import EmailEngine
        email_engine = EmailEngine()

        self.__check_saps(self.detected_plate)
        self.__check_marked(self.detected_plate)

        vehicle = Vehicle.objects.get(id=vehicle_id)
        # for v in vehicle:
        if self.saps_flagged:
            email_engine.send_saps_flag_notification(self.to_address, vehicle)
        vehicle.saps_flagged = self.saps_flagged
        vehicle.save()

        if self.marked:
            for address in self.marked_address:
                email_engine.send_flagged_notification(address, vehicle[0])

        self.tracking_data["vehicle"] = vehicle_id
        tracking_serializer = TrackingSerializer(data=self.tracking_data)
        if tracking_serializer.is_valid():
            track = tracking_serializer.save()
            self.image.vehicle = track.vehicle
            self.image.save()
            #self.vehicle.delete()
            return vehicle
        else:
            return "Error tracking vehicle"

    def __check_for_perfect_match(self):
        """
        Checks for a perfect match and if found then tracks the vehicle and then returns True
        Returns false on no perfect match
        """

        try:
            check_vehicle = Vehicle.objects.get(
                license_plate__iexact=self.detected_plate,
                make__iexact=self.detected_make,
                model__iexact=self.detected_model,
                color__iexact=self.detected_color,
                license_plate_duplicate=False,
            )
        except Vehicle.DoesNotExist:
            return False

        self.tracking_data["vehicle"] = check_vehicle.id
        tracking_serializer = TrackingSerializer(data=self.tracking_data)
        if tracking_serializer.is_valid():
            tracking_serializer.save()
            return check_vehicle
        else:
            return False

    def __save_vehicle(self, temp_plate):
        from email_engine import EmailEngine
        email_engine = EmailEngine()
        self.__check_saps(temp_plate)
        self.__check_marked(temp_plate)
        vehicle_data = {
            "license_plate": temp_plate,
            "make": self.detected_make,
            "model": self.detected_model,
            "color": self.detected_color,
            "saps_flagged": self.saps_flagged,
            "license_plate_duplicate": self.license_plate_duplicate
        }

        accuracy_data = {
            "vehicle": None,
            "make_accuracy": self.make_model_accuracy,
            "model_accuracy": self.make_model_accuracy,
            "color_accuracy": self.color_accuracy,
            "license_plate_accuracy": 0.00,
            "damage_accuracy": self.damage_accuracy
        }

        vehicle_serialzier = VehicleSerializer(data=vehicle_data)
        if vehicle_serialzier.is_valid():
            self.new_vehicle = vehicle_serialzier.save()
            self.image.vehicle = self.new_vehicle
            self.image.save()

            if self.detected_damage_location != "":
                dmg = Damage(vehicle=self.new_vehicle, location=self.detected_damage_location)
                dmg.save()
                # TODO: Steven save the pictures properly

            accuracy_data["vehicle"] = self.new_vehicle.id
            accuracy_data["make_accuracy"] = float("{:.2f}".format(accuracy_data["make_accuracy"]))
            accuracy_data["model_accuracy"] = float("{:.2f}".format(accuracy_data["model_accuracy"]))
            accuracy_data["color_accuracy"] = float("{:.2f}".format(accuracy_data["color_accuracy"]))
          
            accuracy_serializer = AccuracySerializer(data=accuracy_data)
            if accuracy_serializer.is_valid():
                accuracy_serializer.save()
                self.tracking_data["vehicle"] = self.new_vehicle.id
                tracking_serializer = TrackingSerializer(data=self.tracking_data)
                if tracking_serializer.is_valid():
                    tracking_serializer.save() 
                    if self.new_vehicle.license_plate != "":
                        if self.marked:
                            for email in self.marked_address:
                                email_engine.send_flagged_notification(email, self.new_vehicle)
                        if self.saps_flagged:
                            email_engine.send_saps_flag_notification(self.to_address, self.new_vehicle)
                    return self.new_vehicle
                else:
                    return "Error with tracking information"
            else:
                return "Error with accuracy information"
        else:
            return "Error with vehicle information"


    def __get_plate_information(self):
        
        result = self.__recognize_plate_with_api()
        return result

    def __recognize_plate_with_api(self):
        regions = ["za"]

        path = self.image.image.path

        with open(path, 'rb') as fp:
            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                data=dict(regions=regions),  # Optional
                files=dict(upload=fp),
                headers={'Authorization': 'token 8e744c1226777aa96d25e06807b69cbfc03f4c72'})
            res = response.json()
        if res.get("error", None):
            return False
        res = res["results"]
        if len(res) == 0:
            return 1
        return res[0]["plate"]

    def __check_for_duplication_plates(self, license_plate):
        qs = Vehicle.objects.filter(license_plate__iexact=license_plate)

        if qs.count() > 0:
            return qs
        return False

    def __check_saps(self, license_plate):
        self.saps_flagged = saps_API(
            params={
                "license_plate": license_plate
            }
        )
        return self.saps_flagged

    def __check_marked(self, license_plate):
        self.marked = False
        
        obj = MarkedVehicle.objects.filter(license_plate=license_plate)
        if obj.count() > 0:
            self.marked_address = []
            for item in obj:
                self.marked_address.append(item.marked_by.email)
            self.marked = True
        return self.marked

    def should_notify_saps(self):
        if self.saps_flagged:
            return True
        else:
            return False



class VehicleDecisionEngine():
    """
    Custom engine to do stuff with vehicles
    """

    def __init__(self):
        self.similar_iteration = 0

    def get_similar_vehicles(self, vehicle):
        """
        A way to pass in a vehicle and get a list of vehicles ids and similarity scores
        The first pass attempts to find vehicles with atleast 80% similarity then each subsequant iterations loses 20%
        """

        minimum_percentages = {
            "0": 80,
            "1": 60,
            "2": 40,
            "3": 20
        }

        if self.similar_iteration == 4:
            self.similar_iteration = 0
            return False

        small = minimum_percentages[str(self.similar_iteration)]
        self.similar_iteration = self.similar_iteration + 1
        similar_qs = self.__get_similar_vehicle_queryset(vehicle)

        score_engine = ScoringEngine()

        results = []

        for test_case in similar_qs:
            if vehicle.license_plate == "" or test_case.license_plate == "":
                score = score_engine.similarity_comparison_np(test_case, vehicle)
            else:
                score = score_engine.similarity_comparison(test_case, vehicle)

            if score >= small:
                results.append({
                    "vehicle_id": test_case.id,
                    "similarity_score": score
                })

        return results

    def obtain_private_qs(self, vehicle):
        return self.__get_similar_vehicle_queryset(vehicle)

    def __get_similar_vehicle_queryset(self, vehicle):
        """
        Takes in a vehicle and returns a queryset of vehicles that are similar
        """
        serializer = VehicleSerializer(vehicle)
        data = serializer.data

        damage_location = vehicle.damage.all()[0].location

        queryset = Vehicle.objects.filter(
                Q(make__iexact=data["make"])
                | Q(model__exact=data["model"])
                | Q(color__iexact=data["color"])
                | Q(license_plate__iexact=data["license_plate"])
                | Q(damage__location__iexact=damage_location)
        )

        return queryset

    def replace_vehicle(self, to_be_replaced, replacer):
        """
        Takes in two vehicles and replaces the first with the second.
        Simply put, it deletes the first vehicle and set the second ones license_plate to the first if the second
        ones license plate is not available
        """

        temp_license_plate = to_be_replaced.license_plate

        to_be_replaced.delete()

        if replacer.license_plate == "":
            replacer.license_plate = temp_license_plate

        return True


class ScoringEngine():
    """
    A custom class to determine scores for vehicles
    This will also handle the similarity scoring for vehicles without license plates
    """


    def __init__(self):
        # The scoring weights of the engine
        self.weights = {
            "make": 0.2,
            "model": 0.2,
            "license_plate": 0.2,
            "color": 0.2,
            "damage": 0.2
        }

        self.comparison_weights = {
            "make": 0.25,
            "model": 0.25,
            "color": 0.25,
            "damage": 0.25
        }

    def score_vehicle(self, vehicle):
        """
        Returns a percentage based score for the vehicle passed in
        Expects: Vehicle object
        """

        if not vehicle:
            return False

        # Get the related vehicles accuracies
        try:
            accuracy = Accuracy.objects.get(vehicle=vehicle.id)
        except Accuracy.DoesNotExist:
            return False

        vehicle_data = {
            "make": accuracy.make_accuracy,
            "model": accuracy.model_accuracy,
            "color": accuracy.color_accuracy,
            "license_plate": accuracy.license_plate_accuracy,
            "damage": accuracy.damage_accuracy
        }

        self.score = 0
        for key in vehicle_data.keys():
            self.score = self.score + (vehicle_data[key] * self.weights[key])

        return score

    def similarity_comparison_np(self, a, b):
        """
        Used to get a percentage based likliehood that two vehicles are the same vehicle without using their license_plates
        """

        a_damage = a.damage.all()[0]
        b_damage = b.damage.all()[0]

        likelihood = 0

        if a.make.lower() == b.make.lower():
            likelihood = likelihood + (self.comparison_weights["make"] * 100)

        if a.model.lower() == b.model.lower():
            likelihood = likelihood + (self.comparison_weights["model"] * 100)

        if a.color.lower() == b.color.lower():
            likelihood = likelihood + (self.comparison_weights["color"] * 100)

        if a_damage.location == b_damage.location:
            likelihood = likelihood + (self.comparison_weights["damage"] * 100)
        
        if not a_damage and not b_damage:
            likelihood = likelihood + 20

        return likelihood


    def similarity_comparison(self, a, b):
        """
        Used to get vehicle similarity with license plates
        """

        a_damage = a.damage.all()[0]
        b_damage = b.damage.all()[0]

        likelihood = 0

        if a.make.lower() == b.make.lower():
            likelihood = likelihood + (self.weights["make"] * 100)

        if a.model.lower() == b.model.lower():
            likelihood = likelihood + (self.weights["model"] * 100)

        if a.color.lower() == b.color.lower():
            likelihood = likelihood + (self.weights["color"] * 100)

        if a_damage.location == b_damage.location:
            likelihood = likelihood + (self.weights["damage"] * 100)

        if not a_damage and not b_damage:
            likelihood = likelihood + 20

        if a.license_plate.lower() == b.license_plate.lower():
            likelihood = likelihood + (self.weights["license_plate"] * 100)

        return likelihood