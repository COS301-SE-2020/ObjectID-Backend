from .models import Accuracy, Vehicle
from .serializers import VehicleSerializer

from django.db.models import Q



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

        small = minimum_percentages[self.similar_iteration]
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

        if a.license_plate.lower() == b.license_plate.lower():
            likelihood = likelihood + (self.weights["license_plate"] * 100)

        return likelihood