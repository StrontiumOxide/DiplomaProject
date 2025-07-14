from django.urls import path
from Market import views

urlpatterns = [
        # User
        # Получение всех пользователей
    path(route='users/', view=views.get_all_users),
        # Получение, обновления, удаление одного пользователя
    path(route='user/<int:pk>/', view=views.UserView.as_view()),
        # Создание пользователя
    path(route='user/', view=views.UserView.as_view()),

        # Category
    path(route='categories/', view=views.CategoryView.as_view()),  # GET(list), POST
    path(route='categories/<int:pk>/', view=views.CategoryView.as_view()),  # GET(detail), PATCH, DELETE

        # Shop
    path(route='shops/', view=views.ShopView.as_view()), # GET(list), POST
    path(route='shops/<int:pk>/', view=views.ShopView.as_view()), # GET(detail), PATCH, DELETE

        # Product
    path(route='products/', view=views.ProductView.as_view(), name='products'), # GET(list), POST
    path(route='products/<int:pk>/', view=views.ProductView.as_view(), name='product-detail'), # GET(detail), PATCH, DELETE
]
