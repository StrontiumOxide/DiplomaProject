from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django import forms
from .models import User, UserCredentials, Shop, Product, Category, Busket, Order, OrderPosition

# Форма для учётных данных с скрытым паролем
class UserCredentialsForm(forms.ModelForm):
    class Meta:
        model = UserCredentials
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput()
        }

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone_number')
    search_fields = ('last_name', 'first_name', 'email', 'phone_number')
    list_filter = ('last_name',)
    ordering = ('last_name', 'first_name')

@admin.register(UserCredentials)
class UserCredentialsAdmin(admin.ModelAdmin):
    form = UserCredentialsForm
    list_display = ('user', 'login')
    search_fields = ('user__last_name', 'user__first_name', 'login')
    readonly_fields = ('password_display',)
    
    def password_display(self, obj):
        return "********"
    password_display.short_description = 'Пароль'
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'url')
    search_fields = ('title', 'user__last_name', 'user__first_name')
    list_filter = ('user',)
    raw_id_fields = ('user',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_count')
    search_fields = ('title',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Количество товаров'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'shop', 'price', 'quantity')
    list_filter = ('category', 'shop')
    search_fields = ('title', 'description')
    list_editable = ('price', 'quantity')
    raw_id_fields = ('category', 'shop')

# Inline для позиций заказа
class OrderPositionInline(admin.TabularInline):
    model = OrderPosition
    extra = 0
    raw_id_fields = ('product',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'create_at', 'status')
    list_filter = ('status', 'create_at')
    search_fields = ('user__last_name', 'user__first_name')
    inlines = [OrderPositionInline]
    date_hierarchy = 'create_at'

@admin.register(Busket)
class BusketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__last_name', 'product__title')
    list_filter = ('user',)
    raw_id_fields = ('user', 'product')
    