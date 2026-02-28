from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import UserRole


def admin_required(view_func):
    """Декоратор для проверки прав администратора."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация.')
            return redirect('login')
        
        # Проверяем, является ли пользователь администратором
        if not (request.user.role == UserRole.ADMIN or request.user.is_superuser):
            messages.error(request, 'Доступ запрещён. Требуются права администратора.')
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
