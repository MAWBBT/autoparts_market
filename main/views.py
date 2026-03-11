from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import RegistrationForm
from .decorators import admin_required
from .admin_forms import UserEditForm, UserCreateForm, ProductForm, CategoryForm


def home(request):
    """Главная страница."""
    categories = []
    featured_products = []
    try:
        from products.models import Category, Product
        categories = list(Category.objects.all().order_by('name')[:8])
        featured_products = list(
            Product.objects.filter(available=True)
            .select_related('category')
            .order_by('-created')[:8]
        )
    except Exception:
        # Если БД/миграции ещё не готовы — просто показываем статическую главную.
        categories = []
        featured_products = []
    return render(request, 'main/index.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def about(request):
    """Страница «О нас» — информация о компании."""
    return render(request, 'main/about.html')


def register(request):
    """Регистрация пользователя (ФИО, email, телефон, пароль, согласие)."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})


@login_required
def profile(request):
    """Профиль пользователя: данные и ссылка на историю заказов."""
    from .models import UserProfile
    from .forms import ProfileEditForm, PasswordChangeForm
    from cart.models import Order
    
    # Получаем или создаем профиль пользователя
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': getattr(request.user, 'full_name', None) or request.user.email},
    )
    
    # Определяем, какая форма была отправлена
    form_type = request.POST.get('form_type', 'profile')
    
    if request.method == 'POST':
        if form_type == 'password':
            # Обработка изменения пароля
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            profile_form = ProfileEditForm(instance=profile, user=request.user)
            
            if password_form.is_valid():
                password_form.save()
                # Обновляем сессию после смены пароля
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Пароль успешно изменён.')
                return redirect('profile')
        else:
            # Обработка изменения профиля
            profile_form = ProfileEditForm(request.POST, instance=profile, user=request.user)
            password_form = PasswordChangeForm(user=request.user)
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлён.')
                return redirect('profile')
    else:
        profile_form = ProfileEditForm(instance=profile, user=request.user)
        password_form = PasswordChangeForm(user=request.user)

    orders = Order.objects.filter(user=request.user).prefetch_related("items__product").order_by("-created")
    current_orders = [o for o in orders if o.status not in ("issued", "cancelled", "completed")]
    completed_orders = [o for o in orders if o.status in ("issued", "cancelled", "completed")]
    
    return render(request, 'main/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile,
        'current_orders': current_orders,
        'completed_orders': completed_orders,
    })


# ========== АДМИН-ПАНЕЛЬ ==========

@admin_required
def admin_dashboard(request):
    """Главная страница админ-панели."""
    from django.contrib.auth import get_user_model
    from products.models import Product, Category
    from cart.models import Order
    
    User = get_user_model()
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'total_products': Product.objects.count(),
        'available_products': Product.objects.filter(available=True).count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='processing').count(),
    }
    
    recent_orders = Order.objects.select_related('user').order_by('-created')[:5]
    
    return render(request, 'main/admin/dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
    })


@admin_required
def admin_users(request):
    """Управление пользователями."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )
    
    paginator = Paginator(users.order_by('-id'), 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    return render(request, 'main/admin/users.html', {
        'users': users_page,
        'search_query': search_query,
    })


@admin_required
def admin_user_create(request):
    """Создание нового пользователя."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь успешно создан.')
            return redirect('admin_panel:users')
    else:
        form = UserCreateForm()
    
    return render(request, 'main/admin/user_form.html', {
        'form': form,
        'title': 'Создать пользователя',
    })


@admin_required
def admin_user_edit(request, user_id):
    """Редактирование пользователя."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Пользователь {user.email} успешно обновлён.')
            return redirect('admin_panel:users')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'main/admin/user_form.html', {
        'form': form,
        'user': user,
        'title': f'Редактировать пользователя: {user.email}',
    })


@admin_required
def admin_user_delete(request, user_id):
    """Удаление пользователя."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        email = user.email
        user.delete()
        messages.success(request, f'Пользователь {email} удалён.')
        return redirect('admin_panel:users')
    
    return render(request, 'main/admin/user_delete.html', {'user': user})


@admin_required
def admin_products(request):
    """Управление товарами."""
    from products.models import Product
    
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    products = Product.objects.select_related('category').all()
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(article__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    paginator = Paginator(products.order_by('-created'), 20)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    
    from products.models import Category
    categories = Category.objects.all()
    
    return render(request, 'main/admin/products.html', {
        'products': products_page,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
    })


@admin_required
def admin_product_create(request):
    """Создание нового товара."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно создан.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm()
    
    return render(request, 'main/admin/product_form.html', {
        'form': form,
        'title': 'Создать товар',
    })


@admin_required
def admin_product_edit(request, product_id):
    """Редактирование товара."""
    from products.models import Product
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлён.')
            return redirect('admin_panel:products')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'main/admin/product_form.html', {
        'form': form,
        'product': product,
        'title': f'Редактировать товар: {product.name}',
    })


@admin_required
def admin_product_delete(request, product_id):
    """Удаление товара."""
    from products.models import Product
    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Товар "{name}" удалён.')
        return redirect('admin_panel:products')
    
    return render(request, 'main/admin/product_delete.html', {'product': product})


@admin_required
def admin_orders(request):
    """Управление заказами."""
    from cart.models import Order
    
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    orders = Order.objects.select_related('user').prefetch_related('items__product').all()
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    paginator = Paginator(orders.order_by('-created'), 20)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)
    
    from cart.models import ORDER_STATUSES
    
    return render(request, 'main/admin/orders.html', {
        'orders': orders_page,
        'statuses': ORDER_STATUSES,
        'status_filter': status_filter,
        'search_query': search_query,
    })


@admin_required
def admin_order_detail(request, order_id):
    """Детали заказа."""
    from cart.models import Order, ORDER_STATUSES
    
    order = get_object_or_404(Order.objects.select_related('user').prefetch_related('items__product'), id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлён.')
            return redirect('admin_panel:order_detail', order_id=order.id)
    
    return render(request, 'main/admin/order_detail.html', {
        'order': order,
        'statuses': ORDER_STATUSES,
    })


@admin_required
def admin_order_delete(request, order_id):
    """Удаление заказа."""
    from cart.models import Order
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order_id_str = str(order.id)
        order.delete()
        messages.success(request, f'Заказ #{order_id_str} удалён.')
        return redirect('admin_panel:orders')
    
    return render(request, 'main/admin/order_delete.html', {'order': order})


@admin_required
def admin_categories(request):
    """Управление категориями."""
    from products.models import Category
    
    categories = Category.objects.prefetch_related('products').all()
    
    return render(request, 'main/admin/categories.html', {
        'categories': categories,
    })


@admin_required
def admin_category_create(request):
    """Создание новой категории."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана.')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm()
    
    return render(request, 'main/admin/category_form.html', {
        'form': form,
        'title': 'Создать категорию',
    })


@admin_required
def admin_category_edit(request, category_id):
    """Редактирование категории."""
    from products.models import Category
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{category.name}" успешно обновлена.')
            return redirect('admin_panel:categories')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'main/admin/category_form.html', {
        'form': form,
        'category': category,
        'title': f'Редактировать категорию: {category.name}',
    })


@admin_required
def admin_category_delete(request, category_id):
    """Удаление категории."""
    from products.models import Category
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Категория "{name}" удалена.')
        return redirect('admin_panel:categories')
    
    return render(request, 'main/admin/category_delete.html', {'category': category})
