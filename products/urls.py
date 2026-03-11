from django.urls import path
from . import views
from . import api

app_name = 'products'

urlpatterns = [
    path('catalog/', views.catalog_view, name='catalog'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Lab №8 API
    path('api/products/', api.ProductListApi.as_view(), name='api_products_list'),
    path('api/products/create/', api.ProductCreateApi.as_view(), name='api_products_create'),
    path('api/products/<int:pk>/', api.ProductDetailApi.as_view(), name='api_products_detail'),
]
