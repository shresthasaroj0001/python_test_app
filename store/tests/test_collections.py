#pipenv install --dev pytest
#pipenv install --dev pytest-django

from store.models import Collection
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
import pytest
from model_bakery import baker

#client = APIClient() is replaced by fixture from confttest.py

@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection): #passing the parameter
        return api_client.post('/store/collections/', collection)
    return do_create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_not_admin_returns_403(self, api_client, create_collection, authenticate):
        authenticate()
        # api_client.force_authenticate(user={})
        
        response = create_collection({ 'title' : 'a'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client, create_collection, authenticate):
        authenticate(True)
        # api_client.force_authenticate(user=User(is_staff=True))
        response = create_collection({ 'title' : ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None


    def test_if_data_is_valid_returns_201(self, api_client):
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post('/store/collections/', { 'title' : 'valid title'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

    @pytest.mark.skip
    def test_if_user_is_anonymous_returns_401(self):
        #Arrange

        #Act
        client = APIClient()
        response = client.post('/store/collections/',{'title':'a'})

        #Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

#pipenv install --dev model_bakery
#It helps to auto populate the models
@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_collection_exits_returns_200(self, api_client):
        #baker.make(Product)
        #It will auto create dependncy element as well

        #collection = baker.make(Collection)
        #baker.make(Product, collection=collection, _quantity=10) It will make 10 products with same collection

        collection = baker.make(Collection)

        response = api_client.get(f'/store/collections/{collection.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id' : collection.id,
            'title' : collection.title,
            'products_count' :0
        }
                                   
                                  

                                  
