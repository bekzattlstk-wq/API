import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@mail.com',
        password='testpass123'
    )

@pytest.fixture
def auth_client(api_client, user):
    token = AccessToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client

@pytest.fixture
def category():
    from api.models import Category
    return Category.objects.create(
        name='Ноутбуки',
        slug='notebooks'
    )

@pytest.fixture
def product(category, user):
    from api.models import Product
    return Product.objects.create(
        category=category,
        seller=user,
        name='MacBook Pro',
        price=150000.00,
        description='Отличный ноутбук',
        is_available=True,
        in_stock=10
    )
