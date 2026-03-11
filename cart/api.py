from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminUserRole
from accounts.models import User
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .api_serializers import (
    CartSerializer,
    AddToCartSerializer,
    OrderSerializer,
    UpdateOrderStatusSerializer,
)


def _get_or_create_user_cart(user: User) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartGetApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = _get_or_create_user_cart(request.user)
        return Response(CartSerializer(cart).data)


class CartAddApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = AddToCartSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        cart = _get_or_create_user_cart(request.user)
        product = get_object_or_404(Product, id=ser.validated_data["product_id"])
        quantity = ser.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartRemoveApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id: int):
        cart = _get_or_create_user_cart(request.user)
        CartItem.objects.filter(cart=cart, id=item_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class CartClearApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = _get_or_create_user_cart(request.user)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class OrdersCheckoutApi(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = _get_or_create_user_cart(request.user)
        items = list(cart.items.select_related("product"))
        if not items:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        total_products = sum((i.product.price * i.quantity for i in items), Decimal("0"))
        order = Order.objects.create(
            user=request.user,
            total_products=total_products,
            delivery_cost=Decimal("0"),
            total=total_products,
            status="created",
        )
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    product=i.product,
                    quantity=i.quantity,
                    price=i.product.price,
                )
                for i in items
            ]
        )
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrdersCreateApi(APIView):
    """
    Lab №8 endpoint: create order directly from JSON items (without cart).
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        items = request.data.get("items") or []
        if not isinstance(items, list) or not items:
            return Response({"detail": "items[] is required"}, status=status.HTTP_400_BAD_REQUEST)

        product_ids = [i.get("product_id") for i in items]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        if len(products) != len(set(product_ids)):
            return Response({"detail": "Some products not found"}, status=status.HTTP_400_BAD_REQUEST)

        total_products = Decimal("0")
        order_items = []
        for row in items:
            pid = int(row["product_id"])
            qty = int(row.get("quantity", 1))
            if qty < 1:
                return Response({"detail": "quantity must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)
            p = products[pid]
            total_products += p.price * qty
            order_items.append(OrderItem(order_id=None, product=p, quantity=qty, price=p.price))

        order = Order.objects.create(
            user=request.user,
            total_products=total_products,
            delivery_cost=Decimal("0"),
            total=total_products,
            status="created",
        )
        for oi in order_items:
            oi.order = order
        OrderItem.objects.bulk_create(order_items)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrdersMyApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created")
        return Response(OrderSerializer(orders, many=True).data)


class OrdersAdminListApi(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        orders = Order.objects.all().order_by("-created")
        return Response(OrderSerializer(orders, many=True).data)


class OrdersAdminUpdateStatusApi(APIView):
    permission_classes = [IsAdminUserRole]

    def put(self, request, order_id: int):
        ser = UpdateOrderStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = Order.objects.get(id=order_id)
        order.status = ser.validated_data["status"]
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order).data)


class AdminStatisticsApi(APIView):
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        revenue = Order.objects.aggregate(v=Sum("total"))["v"] or Decimal("0")
        return Response(
            {
                "users": User.objects.count(),
                "products": Product.objects.count(),
                "orders": Order.objects.count(),
                "revenue": int(revenue),
            }
        )

