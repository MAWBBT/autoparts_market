from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('users/create/', views.admin_user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.admin_user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.admin_user_delete, name='user_delete'),
    path('products/', views.admin_products, name='products'),
    path('products/create/', views.admin_product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.admin_product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.admin_product_delete, name='product_delete'),
    path('orders/', views.admin_orders, name='orders'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='order_detail'),
    path('orders/<int:order_id>/delete/', views.admin_order_delete, name='order_delete'),
    path('categories/', views.admin_categories, name='categories'),
    path('categories/create/', views.admin_category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.admin_category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.admin_category_delete, name='category_delete'),
]
