from django.urls import path
from Market import views

urlpatterns = [
        # User
    path(route='users/', view=views.get_all_users),
    path(route='user/<int:pk>/', view=views.UserView.as_view()),
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

        # Busket
    path(route='buskets/<int:user_id>/', view=views.BusketView.as_view(), name='user-buskets'), # GET(detail), POST
    path(route='buskets/', view=views.BusketView.as_view(), name='buskets-actions'), # DELETE

        # Order
    path(route='orders/', view=views.OrderView.as_view(), name='orders-list'),
    path(route='orders/<int:order_id>/', view=views.OrderView.as_view(), name='order-detail'),
    path(route='orders/user/<int:user_id>/', view=views.OrderView.as_view(), name='user-orders'),
]
