import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthAPI:

    def test_register_user(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@mail.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert User.objects.filter(username='newuser').exists()

    def test_register_user_password_mismatch(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'new@mail.com',
            'password': 'pass123',
            'password2': 'pass456'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_obtain(self, api_client, user):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_token_obtain_invalid_credentials(self, api_client):
        url = reverse('token_obtain_pair')
        data = {'username': 'wrong', 'password': 'wrong'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, user):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')
        refresh = response.data['refresh']

        url_refresh = reverse('token_refresh')
        response = api_client.post(url_refresh, {'refresh': refresh}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
