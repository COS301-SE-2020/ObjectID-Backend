from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
# Create your tests here.
class VehicleTests(APITestCase):
    def test_add_vehicle_basic(self):

        url = '/api/v1/vehicle/add_vehicle_basic/'
        data = {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
        }
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,200)

    def test_get_vehicle(self):

        url = '/api/v1/vehicle/get_vehicle/'
        data = {
            'license_plate' : 'BE32SNGP'
        }
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,200)

    def test_and_search(self):

        url = '/api/v1/vehicle/and_search/'
        data = {
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }
        response = self.client.post(url,data, format='json')
        self.assertEqual(response.status_code,200)

    # def test_file_recognize(self):

    #     url = '/api/v1/vehicle/file_recognize/'
    #     data = {
    #         'license_plate' : 'BE32SNGP',
    #         'make' : 'Toyota',
    #         'model' : 'Corolla',
    #         'color' : 'White'
    #     }
    #     response = self.client.post(url,data)
    #     self.assertEqual(response.status_code,200)

    