from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
import requests

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

    def test_or_search(self):

        url = '/api/v1/vehicle/search_or/'
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

    def test_file_recognize(self):
        import pathlib
        url = '/api/v1/vehicle/file_recognize/'
        


        # response = self.client.post(url,data)
        

        path = pathlib.Path(__file__).parent.absolute()

        actual_path ='{}/test_images/2015-BMW-320d-xDrive-Touring-test-drive-67.jpg'.format(path)

        files = [
        ('file', open("{}".format(actual_path), 'rb'))
        ]
        data = {
             'file' : files[0]
        }

        response = self.client.post(url, data=data, files=files)


        self.assertEqual(response.status_code, 200)