from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from .models import User, UserCredentials, Category, Shop
from .serializers import UserSerializer, CategorySerializer,ShopCreateSerializer, ShopDetailSerializer


def main_page(request: HttpRequest) -> HttpResponse:
    """Функция, отвечающая за отображение главной страницы"""

    return render(request=request, template_name='market/main_page.html')


@api_view(http_method_names=['GET'])
def get_all_users(request: HttpRequest) -> Response:
    """Функция по получению всех пользователей"""

    users = User.objects.all()
    ser_users = UserSerializer(users, many=True)
    return Response(ser_users.data)


class UserView(APIView):
    """Класс для работы с User и UserCredentials"""

    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Получение одного пользователя"""

        try:
            pk = kwargs['pk']  # Получаем pk из URL
            user = User.objects.get(id=pk)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request: HttpRequest) -> Response:
        """Создание пользователя и его учётных данных"""

        data = request.data.copy()
        login = data.get('login')
        password = data.get('password')

        if not login or not password:
            return Response(
                {"error": "Login and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Валидация и создание пользователя
        user_serializer = UserSerializer(data=data)
        if user_serializer.is_valid():
            user = user_serializer.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Создание учётных данных
        UserCredentials.objects.create(user=user, login=login, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    def patch(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Частичное обновление пользователя"""

        try:
            pk = kwargs.get('pk')
            user = User.objects.get(id=pk)
            
            # Частичное обновление через сериализатор
            serializer = UserSerializer(user, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
    def delete(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Удаление пользователя и его учётных данных"""

        permission_classes = [permissions.IsAuthenticated]
        try:
            pk = kwargs.get('pk')
            user = User.objects.get(id=pk)
            user.delete()

            return Response(
                {"message": f"Пользователь {user.first_name} {user.last_name} удалён"},
                status=status.HTTP_200_OK
            )
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        

class CategoryView(APIView):
    """
    API для работы с категориями товаров
    Поддерживает: GET, POST, PATCH, DELETE
    """
    
    def get(self, request, pk=None):
        """
        Получение одной категории (по pk) или списка всех категорий
        """
        if pk:
            try:
                category = Category.objects.get(pk=pk)
                serializer = CategorySerializer(category)
                return Response(serializer.data)
            except Category.DoesNotExist:
                return Response(
                    {"error": "Category not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

    def post(self, request):
        """
        Создание новой категории
        """
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Частичное обновление категории
        """
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """
        Удаление категории
        """
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(
                {"message": f"Category '{category.title}' deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        

class ShopView(APIView):
    def get(self, request, pk=None):
        if pk:
            try:
                shop = Shop.objects.get(pk=pk)
                serializer = ShopDetailSerializer(shop)
                return Response(serializer.data)
            except Shop.DoesNotExist:
                return Response(
                    {"error": "Shop not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        shops = Shop.objects.all()
        serializer = ShopDetailSerializer(shops, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShopCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(pk=serializer.validated_data['user_id'])
                
                # Проверяем, не имеет ли пользователь уже магазин
                if hasattr(user, 'shops'):
                    return Response(
                        {"error": "This user already owns a shop"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                shop = Shop.objects.create(
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data.get('description', ''),
                    url=serializer.validated_data.get('url', ''),
                    user=user
                )
                
                return Response(
                    ShopDetailSerializer(shop).data,
                    status=status.HTTP_201_CREATED
                )
            
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Частичное обновление магазина
        """
        try:
            shop = Shop.objects.get(pk=pk)
            serializer = ShopCreateSerializer(shop, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Shop.DoesNotExist:
            return Response(
                {"error": "Магазин не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """
        Удаление магазина
        """
        try:
            shop = Shop.objects.get(pk=pk)
            shop.delete()
            return Response(
                {"message": f"Магазин '{shop.title}' удален"},
                status=status.HTTP_200_OK
            )
        except Shop.DoesNotExist:
            return Response(
                {"error": "Магазин не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        