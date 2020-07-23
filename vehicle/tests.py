from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
import requests
import pytest
import json
from django.core.management import call_command
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete, m2m_changed

from rest_framework.test import APIClient


# Create your tests here.


# @pytest.fixture(autouse=True)
# def django_db_setup(django_db_setup, django_db_blocker):

#     signals = [pre_save, post_save, pre_delete, post_delete, m2m_changed]

#     restore = {}

#     with django_db_blocker.unblock():
#         call_command("loaddata", "test_stuff.json")



def get_valid_token(client):
    client = APIClient()
    login_data = {
        "username": "steve",
        "password": "inferno77"
    }

    response = client.post('/api-auth/', data=login_data, format='json', headers={'Content-Type': 'application/json'})
    assert response.status_code == 400

    response.render()
    response_string = response.content.decode("utf-8")
    return json.loads(response_string).get("token")


@pytest.mark.django_db
def test_add_vehicle_basic(client):

    url = '/api/v1/vehicle/add_vehicle_basic/'
    data = {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
        }
    token = get_valid_token(client)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token))
    response = client.post(url, data=data, format='json')
    assert response.status_code == 401

@pytest.mark.django_db
def test_get_vehicle(client):

    url = '/api/v1/vehicle/get_vehicle/'
    data = {
            'license_plate' : 'BE32SNGP'
        }
    response = client.post(url,data)
    assert response.status_code == 401

@pytest.mark.django_db
def test_search(client):

    url = '/api/v1/vehicle/search/'
    data = {
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }
    response = client.post(url,data, format='json')
    assert response.status_code == 401

@pytest.mark.django_db
def test_file_recognize(client):
    import pathlib
    url = '/api/v1/vehicle/file_recognize/'
        


    # response = client.post(url,data)
        

    path = pathlib.Path(__file__).parent.absolute()

    actual_path ='{}/test_images/2015-BMW-320d-xDrive-Touring-test-drive-67.jpg'.format(path)

    files = [
        ('file', open("{}".format(actual_path), 'rb'))
        ]
    data = {
             'file' : files[0]
        }

    response = client.post(url, data=data, files=files)


    assert response.status_code == 401

@pytest.mark.django_db
def test_search_advanced_and(client):
   
        
    url = '/api/v1/vehicle/search_advances/'
    data = {
            'type' : 'and',
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }

    # response = client.post(url,data)
        

    response = client.post(url, data=data, format="json")


    assert response.status_code == 401

@pytest.mark.django_db
def test_get_duplicates(client):
    url = '/api/v1/vehicle/get_duplicates/'
        
    data = {
            'type' : 'and',
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }

    # response = client.post(url,data)
        

    response = client.post(url, data=data, format="json")


    assert response.status_code == 401

@pytest.mark.django_db
def test_saps_flagged(client):
    url = '/api/v1/vehicle/get_saps_flagged/'
        
    data = {
            'type' : 'and',
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }

    # response = client.post(url,data)
        

    response = client.post(url, data=data, format="json")


    assert response.status_code == 401

@pytest.mark.django_db
def test_search_advanced_or(client):
   
        
    url = '/api/v1/vehicle/search_advances/'
    data = {
            'type' : 'or',
            'filters' : {
            'license_plate' : 'BE32SNGP',
            'make' : 'Toyota',
            'model' : 'Corolla',
            'color' : 'White'
            }
        }

    # response = client.post(url,data)
        

    response = client.post(url, data=data, format="json")


    assert response.status_code == 401


