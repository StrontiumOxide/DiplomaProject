from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
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
from .serializers import (
    UserSerializer, 
    CategorySerializer,
    ShopCreateSerializer, 
    ShopDetailSerializer, 
    ProductSerializer,
    BusketSerializer,
    OrderSerializer
)


def main_page(request: HttpRequest) -> HttpResponse:
    """Функция, отвечающая за отображение главной страницы"""

    return render(request=request, template_name='market/main_page_2.html')


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
        

class ProductView(APIView):
    """
    API для работы с товарами (GET, POST, PATCH, DELETE)
    Наследуется от базового APIView
    """
    
    def get(self, request, pk=None, format=None):
        """
        Обработка GET-запросов:
        - pk=None: список всех товаров
        - pk указан: детали одного товара
        """
        if pk is not None:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductSerializer(product)
                return Response(serializer.data)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Товар не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Создание нового товара (POST)
        """
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk, format=None):
        """
        Частичное обновление товара (PATCH)
        """
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Товар не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk, format=None):
        """
        Удаление товара (DELETE)
        """
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(
                {"message": f"Продукт '{product.title}' удален"},
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Товар не найден"},
                status=status.HTTP_404_NOT_FOUND
            )


class BusketView(APIView):
    """
    API для работы с корзиной пользователя
    Поддерживает методы: GET (по user_id), POST, DELETE
    """
    
    def get(self, request, user_id, format=None):
        """
        Получение корзины пользователя по ID
        """
        user = get_object_or_404(User, id=user_id)
        queryset = Busket.objects.filter(user=user)
        serializer = BusketSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Добавление товара в корзину с проверкой:
        1. Что товар существует
        2. Что товара достаточно на складе
        3. Что товар еще не добавлен в корзину
        """
        serializer = BusketSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            # Проверка наличия товара в магазине
            if product.quantity < quantity:
                return Response(
                    {
                        "error": f"Недостаточно товара. Доступно: {product.quantity}",
                        "available": product.quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверка на дубликат
            if Busket.objects.filter(user=user, product=product).exists():
                return Response(
                    {"error": "Этот товар уже есть в корзине"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        """
        Удаление продукта из корзины
        Требуемые параметры: user_id и product_id в теле запроса
        """
        try:
            user_id = request.data.get('user_id')
            product_id = request.data.get('product_id')
            
            if not user_id or not product_id:
                return Response(
                    {"error": "Требуются user_id и product_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            busket_item = Busket.objects.get(user_id=user_id, product_id=product_id)
            busket_item.delete()
            return Response(
                {"message": "Товар удален"},
                status=status.HTTP_200_OK
                )
            
        except Busket.DoesNotExist:
            return Response(
                {"error": "Товар не найден в корзине"},
                status=status.HTTP_404_NOT_FOUND
            )
        

class OrderView(APIView):
    def get(self, request, user_id=None):
        """
        Получение всех заказов пользователя
        GET /api/orders/?user_id=<id>
        """
        if not user_id:
            return Response(
                {"error": "Не указан user_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = Order.objects.filter(user_id=user_id).prefetch_related('positions')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request):
        """
        Создание заказа из корзины
        POST /api/orders/ { "user": <id> }
        """
        try:
            user_id = request.data.get('user')
            if not user_id:
                return Response(
                    {"error": "Требуется ID пользователя"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = get_object_or_404(User, id=user_id)
            busket_items = Busket.objects.filter(user=user)
            
            if not busket_items.exists():
                return Response(
                    {"error": "Корзина пуста"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            order = Order.objects.create(user=user, status='created')
            not_added_items = []
            
            for item in busket_items:
                if item.product.quantity >= item.quantity:
                    OrderPosition.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity
                    )
                    item.product.quantity -= item.quantity
                    item.product.save()
                    item.delete()
                else:
                    not_added_items.append({
                        "product_id": item.product.id,
                        "available": item.product.quantity,
                        "requested": item.quantity
                    })

            response_data = {
                "order_id": order.id,
                "status": order.status,
                "not_added": not_added_items
            }

            if not_added_items:
                response_data["warning"] = "Некоторые товары остались в корзине из-за недостатка на складе"

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, order_id):
        """
        Удаление заказа
        DELETE /api/orders/<id>/
        """
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)