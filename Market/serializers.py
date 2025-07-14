from rest_framework import serializers
from .models import (
    User, 
    UserCredentials, 
    Category, 
    Shop, 
    Product, 
    Busket, 
    Order, 
    OrderPosition
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'address']


class UserCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCredentials
        fields = ['id', 'user', 'login', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Скрываем пароль в ответах API
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class ShopCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Shop
        fields = ['title', 'description', 'url', 'user_id']
        extra_kwargs = {
            'url': {'required': False}
        }

class ShopDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Shop
        fields = ['id', 'title', 'description', 'url', 'user']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    shop = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all())
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'category', 'description', 'shop', 'quantity', 'price']

    def to_representation(self, instance):
        """Переопределяем вывод для получения вложенных данных при GET"""
        response = super().to_representation(instance)
        response['category'] = CategorySerializer(instance.category).data
        response['shop'] = ShopDetailSerializer(instance.shop).data
        return response


class BusketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Busket
        fields = ['id', 'user', 'product', 'quantity']
        
    def to_representation(self, instance):
        """Добавляем детализированные данные при выводе"""
        from .serializers import UserSerializer  # Ленивый импорт чтобы избежать циклических зависимостей
        
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        data['product'] = {
            'id': instance.product.id,
            'title': instance.product.title,
            'price': instance.product.price
        }
        return data
    

class OrderPositionSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.IntegerField(source='product.price', read_only=True)

    class Meta:
        model = OrderPosition
        fields = ['id', 'product', 'product_title', 'product_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    positions = OrderPositionSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)  # Явно указываем поле

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'created_at', 'status', 'positions']
        read_only_fields = ['created_at']  # Поле только для чтения
