from .models import Accuracy, Vehicle




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
            "make": 0.2,
            "model": 0.2,
            "color": 0.2,
            "damage": 0.2
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

    def similarity_comparison(self, a, b):
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