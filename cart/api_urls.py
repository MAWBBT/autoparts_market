from django.urls import path

from . import api


urlpatterns = [
    # Cart API (Lab №9)
    path("api/cart/", api.CartGetApi.as_view(), name="api_cart_get"),
    path("api/cart/add/", api.CartAddApi.as_view(), name="api_cart_add"),
    path("api/cart/remove/<int:item_id>/", api.CartRemoveApi.as_view(), name="api_cart_remove"),
    path("api/cart/clear/", api.CartClearApi.as_view(), name="api_cart_clear"),

    # Orders API (Lab №8/9)
    path("api/orders/checkout/", api.OrdersCheckoutApi.as_view(), name="api_orders_checkout"),
    path("api/orders/create/", api.OrdersCreateApi.as_view(), name="api_orders_create"),
    path("api/orders/my/", api.OrdersMyApi.as_view(), name="api_orders_my"),
    path("api/orders/", api.OrdersAdminListApi.as_view(), name="api_orders_admin_list"),
    path("api/orders/<int:order_id>/status/", api.OrdersAdminUpdateStatusApi.as_view(), name="api_orders_admin_status"),

    # Admin statistics (Lab №9)
    path("api/admin/statistics/", api.AdminStatisticsApi.as_view(), name="api_admin_statistics"),
]

