from django.core.management.base import BaseCommand
from Market.models import (
    User, UserCredentials, Shop, 
    Category, Product, Busket,
    Order, OrderPosition
)
from faker import Faker
import random
from datetime import timedelta
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Fill database with consistent test data maintaining all relationships'

    def handle(self, *args, **options):
        fake = Faker('ru_RU')
        
        self.stdout.write("Creating consistent test data...")
        
        # Очистка данных в правильном порядке (с учетом зависимостей)
        self.clear_data()
        
        # 1. Создаем пользователей и их учетные данные
        users = []
        for i in range(10):
            user = User.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                phone_number=f'+79{random.randint(100000000, 999999999)}',
                email=f'{fake.user_name()}{i}@example.com',
                address=fake.address()
            )
            
            UserCredentials.objects.create(
                user=user,
                login=user.email.split('@')[0],
                password='testpass123'
            )
            
            users.append(user)
            self.stdout.write(f'Created user: {user.first_name} {user.last_name}')

        # 2. Создаем владельцев магазинов (первые 5 пользователей)
        shop_owners = users[:5]
        
        # 3. Создаем магазины для каждого владельца
        shops = []
        for i, owner in enumerate(shop_owners):
            shop = Shop.objects.create(
                title=f"{fake.company()} {i+1}",
                description=f"Лучший магазин {fake.catch_phrase()}",
                url=f"https://{fake.domain_name()}",
                user=owner
            )
            shops.append(shop)
            self.stdout.write(f'Created shop: {shop.title} (owner: {owner.first_name})')

        # 4. Создаем категории товаров
        categories = [
            Category.objects.create(title="Электроника"),
            Category.objects.create(title="Одежда"),
            Category.objects.create(title="Книги"),
            Category.objects.create(title="Продукты"),
            Category.objects.create(title="Бытовая техника")
        ]
        
        # 5. Создаем товары с привязкой к магазинам и категориям
        products = []
        product_titles = {
            "Электроника": ["Смартфон", "Ноутбук", "Наушники", "Планшет"],
            "Одежда": ["Футболка", "Джинсы", "Куртка", "Обувь"],
            "Книги": ["Роман", "Детектив", "Фэнтези", "Учебник"],
            "Продукты": ["Молоко", "Хлеб", "Фрукты", "Овощи"],
            "Бытовая техника": ["Холодильник", "Пылесос", "Чайник", "Микроволновка"]
        }
        
        for category in categories:
            for title in product_titles[category.title]:
                for shop in shops:
                    product = Product.objects.create(
                        title=f"{title} {fake.word()}",
                        category=category,
                        description=fake.text(max_nb_chars=100),
                        shop=shop,
                        quantity=random.randint(10, 100),
                        price=random.randint(100, 10000) if category.title != "Продукты" else random.randint(50, 500)
                    )
                    products.append(product)
                    self.stdout.write(f'Created product: {product.title} in {shop.title}')

        # 6. Заполняем корзины для всех пользователей
        for user in users:
            # Каждый пользователь получает 1-3 случайных товара в корзину
            selected_products = random.sample(products, random.randint(1, 3))
            
            for product in selected_products:
                Busket.objects.create(
                    user=user,
                    product=product,
                    quantity=random.randint(1, 3)
                )
            self.stdout.write(f'Created busket for {user.first_name} with {len(selected_products)} items')

        # 7. Создаем заказы (только для пользователей, у которых есть товары в корзине)
        for user in users:
            if random.random() > 0.7:  # 30% вероятность создания заказа
                # Получаем товары из корзины пользователя
                busket_items = Busket.objects.filter(user=user)
                
                if busket_items.exists():
                    order = Order.objects.create(
                        user=user,
                        status=random.choice(['created', 'completed', 'canceled']),
                        create_at=now() - timedelta(days=random.randint(1, 30))
                    )
                    
                    for item in busket_items:
                        OrderPosition.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity
                        )
                        
                        # Если заказ завершен, уменьшаем количество товара
                        if order.status == 'completed':
                            item.product.quantity -= item.quantity
                            item.product.save()
                    
                    # Очищаем корзину после создания заказа
                    busket_items.delete()
                    
                    self.stdout.write(f'Created order #{order.id} for {user.first_name} with {busket_items.count()} items')

        self.stdout.write(self.style.SUCCESS('Database successfully filled with consistent data!'))

    def clear_data(self):
        """Очистка данных с учетом зависимостей"""
        models = [
            OrderPosition, Order, Busket, 
            Product, Shop, UserCredentials, 
            User, Category
        ]
        
        for model in models:
            model.objects.all().delete()
            self.stdout.write(f'Cleared {model.__name__}')
            