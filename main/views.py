from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm


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
    UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'full_name': request.user.get_full_name() or request.user.get_username()},
    )
    return render(request, 'main/profile.html')
