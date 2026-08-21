import pytest
from django.urls import reverse
from rest_framework import status
from api.models import Product


@pytest.mark.django_db
class TestProductsAPI:

    def test_get_products_list(self, api_client, product):
        url = reverse('product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'MacBook Pro'

    def test_get_product_detail(self, api_client, product):
        url = reverse('product-detail', args=[product.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == product.id
        assert 'category_detail' in response.data

    def test_create_product_unauthorized(self, api_client, category, user):
        url = reverse('product-list')
        data = {
            'name': 'Новый товар',
            'price': 999.00,
            'category': category.id,
            'seller': user.id,
            'description': 'Описание',
            'is_available': True,
            'in_stock': 5
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_product_authorized(self, auth_client, category, user):
        url = reverse('product-list')
        data = {
            'name': 'Новый товар',
            'price': 999.00,
            'category': category.id,
            'seller': user.id,
            'description': 'Описание',
            'is_available': True,
            'in_stock': 5
        }
        response = auth_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Новый товар'

    def test_update_product_patch(self, auth_client, product):
        url = reverse('product-detail', args=[product.id])
        data = {'price': 140000.00}
        response = auth_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['price'] == '140000.00'

    def test_update_product_put(self, auth_client, product):
        url = reverse('product-detail', args=[product.id])
        data = {
            'name': 'MacBook Pro 2026',
            'price': 160000.00,
            'category': product.category.id,
            'seller': product.seller.id,
            'description': 'Новое описание',
            'is_available': False,
            'in_stock': 3
        }
        response = auth_client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'MacBook Pro 2026'

    def test_delete_product(self, auth_client, product):
        url = reverse('product-detail', args=[product.id])
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(id=product.id).exists()

    def test_product_filter_by_category(self, api_client, product, category):
        url = reverse('product-list') + f'?category={category.id}'
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_product_search(self, api_client, product):
        url = reverse('product-list') + '?search=Mac'
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_product_ordering(self, api_client, product):
        url = reverse('product-list') + '?ordering=-price'
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data[0]['price'] == '150000.00'