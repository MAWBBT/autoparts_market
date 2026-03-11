from rest_framework import generics

from accounts.permissions import IsAdminOrReadOnly
from .models import Product
from .serializers import ProductSerializer


class ProductListApi(generics.ListAPIView):
    queryset = Product.objects.all().order_by("-created")
    serializer_class = ProductSerializer
    permission_classes = []


class ProductCreateApi(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductDetailApi(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

