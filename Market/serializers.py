from rest_framework import serializers
from .models import User, UserCredentials, Category, Shop


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
