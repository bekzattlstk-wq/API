import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestOrdersAPI:

    def test_get_orders_unauthorized(self, api_client):
        url = reverse('order-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_orders_authorized(self, auth_client):
        url = reverse('order-list')
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_order(self, auth_client, product):
        url = reverse('order-list')
        data = {
            'products': [{'product': product.id, 'quantity': 2}]
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED