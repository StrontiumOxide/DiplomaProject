from django.db import models


class User(models.Model):
    """Стандартная модель пользователя"""

    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=50, verbose_name='Номер телефона')
    email = models.EmailField(max_length=50, verbose_name='Email')
    address = models.CharField(verbose_name='Адрес доставки')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class UserCredentials(models.Model):
    """Модель секретных данных пользователя"""

    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='credentials')
    login = models.CharField(max_length=50, verbose_name='Логин')
    password = models.CharField(verbose_name='Пароль')

    class Meta:
        verbose_name = 'Учётные данные'
        verbose_name_plural = 'Учётные данные'
        ordering = ['login']

    def __str__(self):
        return f"Учётные данные {self.user}"


class Shop(models.Model):
    """Стандартная модель магазина"""

    title = models.CharField(max_length=50, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    url = models.URLField(verbose_name='Ссылка')
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, verbose_name='Владелец', related_name='shops')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} (владелец: {self.user})"
    

class Category(models.Model):
    """Стандартная модель категорий товаров"""

    title = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"


class Product(models.Model):
    """Стандартная модель товара из магазина"""

    title = models.CharField(max_length=100, verbose_name='Название')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    description = models.TextField(verbose_name='Описание')
    shop = models.ForeignKey(to=Shop, on_delete=models.CASCADE, verbose_name='Магазин', related_name='products')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"
    

class Busket(models.Model):
    """Стандартная модель корзины"""

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='buskets')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='buskets')
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        unique_together = [['user', 'product']]
        
    def __str__(self):
        return f"Корзина покупателя: {self.user}"


class Order(models.Model):
    """Стандартная модель заказа"""

    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='Покупатель', related_name='orders')
    create_at = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        
    def __str__(self):
        return f"Заказ покупателя: {self.user}"


class OrderPosition(models.Model):
    """Стандартная модель позиций заказа"""

    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='positions')
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='orders')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        
    def __str__(self):
        return f"Позиции заказа: {self.order}"
