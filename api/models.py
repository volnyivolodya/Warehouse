from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class ApiUser(AbstractUser):
    """
    Модель пользователя (ApiUser) с расширенными полями.

    Поля:
    - group: Роль пользователя (Продавец или Покупатель).
    """
    ROLE_CHOICES = [
        ('seller', 'Продавец'),
        ('buyer', 'Покупатель'),
    ]
    group = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    def __str__(self):
        return self.username


class Warehouse(models.Model):
    """
    Модель склада (Warehouse).

    Поля:
    - name: Название склада.
    """
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """
    Модель продукта (Product).

    Поля:
    - name: Название продукта.
    - warehouse: Склад, на котором хранится продукт (связь с моделью Warehouse).
    - quantity: Количество продукта на складе (минимальное значение 1).
    """
    name = models.CharField(max_length=255, default='Default Name')
    warehouse = models.ForeignKey(Warehouse, related_name="products", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"Продукт: {self.name}. Склад: {self.warehouse.name}. Количество: {self.quantity}"


class Shipment(models.Model):
    """
    Модель отгрузки (Shipment).

    Поля:
    - product: Продукт, который отгружается (связь с моделью Product).
    """
    product = models.ForeignKey(Product, related_name='shipments', on_delete=models.CASCADE)

    def __str__(self):
        return f"Склад: {self.product.warehouse.name}; Продукт: {self.product.name}; Количество: {self.product.quantity}"
