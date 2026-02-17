from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category

CATALOG_PAGE_SIZE = 12


def catalog_view(request):
    """Отображение каталога товаров (фильтр по категории, поиск, сортировка, пагинация)."""
    products = Product.objects.filter(available=True).select_related('category')
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(article__icontains=query)
        )
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')
    paginator = Paginator(products, CATALOG_PAGE_SIZE)
    page = request.GET.get('page')
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    context = {
        'products': products_page,
        'categories': Category.objects.all(),
        'sort': sort_by,
        'query': query or '',
        'category_slug': category_slug or '',
    }
    return render(request, 'products/catalog.html', context)


def product_detail(request, slug):
    """Детальная страница товара."""
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'products/product_detail.html', {'product': product})


def category_detail(request, slug):
    """Товары конкретной категории."""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)
