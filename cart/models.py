from django.db import models
from django.conf import settings
from decimal import Decimal
from products.models import Product

ORDER_STATUSES = [
    # Lab №9 base statuses
    ("created", "Создан"),
    ("processing", "В обработке"),
    ("sent", "Отправлен"),
    ("completed", "Завершен"),
    # Existing project statuses (keep for compatibility with templates)
    ("accepted", "Принято поставщиком"),
    ("delivered_branch", "Доставлен в филиал"),
    ("issued", "Выдан"),
    ("cancelled", "Отменен"),
]


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUSES, default="created")
    full_name = models.CharField(max_length=200, verbose_name='ФИО получателя', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', blank=True, null=True)
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Город', blank=True, null=True)
    address = models.CharField(max_length=300, verbose_name='Улица, дом, квартира', blank=True, null=True)
    postal_code = models.CharField(max_length=20, verbose_name='Индекс', blank=True, null=True)
    payment_method = models.CharField(max_length=100, verbose_name='Способ оплаты', blank=True, null=True)
    delivery_method = models.CharField(max_length=100, verbose_name='Способ доставки', blank=True, null=True)
    comment = models.TextField(verbose_name='Комментарий', blank=True, null=True)
    total_products = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Заказ #{self.id} от {self.created:%d.%m.%Y}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.price * self.quantity
