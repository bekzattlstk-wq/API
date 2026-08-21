from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Product, Order, OrderItem

User = get_user_model()




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


# ============================================================
# 2️⃣ ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР (Product с категорией и продавцом)
# ============================================================

class ProductSerializer(serializers.ModelSerializer):

    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    # ✅ ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — показывает ВСЕ данные категории
    category_detail = CategorySerializer(source='category', read_only=True)

    # ✅ ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — показывает данные продавца
    seller_detail = UserSerializer(source='seller', read_only=True)

    # ✅ ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — количество товаров в категории
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'description',
            'category', 'category_detail',  # ← ВЛОЖЕННЫЙ
            'seller', 'seller_detail',  # ← ВЛОЖЕННЫЙ
            'is_available', 'in_stock',
            'created_at', 'products_count'
        ]

    def get_products_count(self, obj):
        """Количество товаров в категории"""
        return obj.category.products.count()


# ============================================================
# 3️⃣ ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР (Order с товарами)
# ============================================================

class OrderItemSerializer(serializers.ModelSerializer):
    # ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — показывает товар
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    # ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — показывает пользователя
    user_detail = UserSerializer(source='user', read_only=True)

    # ВЛОЖЕННЫЙ СЕРИАЛИЗАТОР — показывает все товары в заказе
    items = OrderItemSerializer(many=True, read_only=True)
    products = OrderItemSerializer(many=True, write_only=True)

    # Дополнительное поле
    total_products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_detail',
            'total_price', 'created_at',
            'items', 'products', 'total_products'
        ]
        read_only_fields = ['total_price', 'created_at']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        total_price = 0

        for item_data in products_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
            )
            total_price += price * quantity

        order.total_price = total_price
        order.save(update_fields=['total_price'])
        return order

    def get_total_products(self, obj):
        """Общее количество товаров в заказе"""
        return obj.items.count()


# ============================================================
# 4️⃣ РЕГИСТРАЦИЯ
# ============================================================

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
