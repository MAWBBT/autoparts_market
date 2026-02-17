from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
import json

DELIVERY_COST = Decimal('300')  # фиксированная стоимость доставки
FREE_DELIVERY_THRESHOLD = Decimal('5000')  # бесплатно от суммы


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        delivery_cost = total_with_delivery = Decimal('0')
    else:
        delivery_cost = Decimal('0') if cart.total_price >= FREE_DELIVERY_THRESHOLD else DELIVERY_COST
        total_with_delivery = cart.total_price + delivery_cost
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'delivery_cost': delivery_cost,
        'total_with_delivery': total_with_delivery,
    })


@require_POST
def add_to_cart(request):
    if request.content_type == 'application/json':
        data = json.loads(request.body)
    else:
        data = request.POST
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={'quantity': quantity},
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True, 'cart_total': cart.total_items,
            'message': f'Товар «{product.name}» добавлен в корзину',
        })
    return redirect('cart:cart')


@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return redirect('cart:cart')


@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity < 1:
        cart_item.delete()
        return redirect('cart:cart')
    cart_item.quantity = quantity
    cart_item.save()
    return redirect('cart:cart')


def checkout(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.info(request, 'Корзина пуста.')
        return redirect('cart:cart')
    delivery_cost = Decimal('0') if cart.total_price >= FREE_DELIVERY_THRESHOLD else DELIVERY_COST
    total_with_delivery = cart.total_price + delivery_cost
    initial = {}
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        p = request.user.profile
        initial = {
            'full_name': p.full_name,
            'email': request.user.email,
            'phone': p.phone or '',
        }
    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            order = Order(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                postal_code=form.cleaned_data.get('postal_code', ''),
                payment_method=form.cleaned_data['payment_method'],
                delivery_method=form.cleaned_data['delivery_method'],
                comment=form.cleaned_data.get('comment', ''),
                total_products=cart.total_price,
                delivery_cost=delivery_cost,
                total=total_with_delivery,
            )
            order.save()
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                )
            cart.items.all().delete()
            messages.success(request, f'Заказ #{order.id} оформлен.')
            return redirect('cart:order_detail', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)
    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'form': form,
        'delivery_cost': delivery_cost,
        'total_with_delivery': total_with_delivery,
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    current = [o for o in orders if o.status not in ('issued', 'cancelled')]
    completed = [o for o in orders if o.status in ('issued', 'cancelled')]
    return render(request, 'cart/order_list.html', {
        'current_orders': current,
        'completed_orders': completed,
    })


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_authenticated and order.user != request.user:
        return redirect('home')
    if not request.user.is_authenticated and order.session_key != request.session.session_key:
        return redirect('home')
    return render(request, 'cart/order_detail.html', {'order': order})


@require_POST
@login_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status not in ('processing', 'accepted', 'delivered_branch'):
        messages.warning(request, 'Этот заказ нельзя отменить.')
        return redirect('cart:order_list')
    order.status = 'cancelled'
    order.save()
    messages.success(request, 'Заказ отменён.')
    return redirect('cart:order_list')


@login_required
def order_repeat(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = get_or_create_cart(request)
    for oi in order.items.all():
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=oi.product, defaults={'quantity': oi.quantity},
        )
        if not created:
            item.quantity += oi.quantity
            item.save()
    messages.success(request, 'Товары из заказа добавлены в корзину.')
    return redirect('cart:cart')
