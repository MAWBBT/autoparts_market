from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'status', 'total', 'created']
    list_filter = ['status', 'created']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['total_products', 'delivery_cost', 'total', 'created']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order']


admin.site.register(Cart)
admin.site.register(CartItem)
