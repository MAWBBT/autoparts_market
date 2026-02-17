from .views import get_or_create_cart


def cart_total(request):
    """Добавляет в контекст шаблонов количество товаров в корзине и саму корзину."""
    if not hasattr(request, 'user') or not request.user:
        return {'cart_total_items': 0, 'cart': None}
    try:
        cart = get_or_create_cart(request)
        return {'cart_total_items': cart.total_items, 'cart': cart}
    except Exception:
        return {'cart_total_items': 0, 'cart': None}
