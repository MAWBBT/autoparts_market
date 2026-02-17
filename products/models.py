from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория',
    )
    article = models.CharField(
        max_length=50,
        verbose_name='Артикул',
        blank=True,
        help_text='Например: BRK-001, OIL-005',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        verbose_name='Изображение',
        blank=True,
        null=True,
    )
    stock = models.PositiveIntegerField(verbose_name='Количество на складе', default=0)
    delivery_days = models.CharField(
        max_length=50,
        verbose_name='Срок доставки при отсутствии',
        blank=True,
        help_text='Например: 3 дня',
    )
    available = models.BooleanField(default=True, verbose_name='Доступен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0
