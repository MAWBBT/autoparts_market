from django import forms
from django.contrib.auth import get_user_model
from accounts.models import UserRole
from products.models import Product, Category
from cart.models import Order

User = get_user_model()


class UserEditForm(forms.ModelForm):
    """Форма для редактирования пользователя.
    
    ВАЖНО: Администратор не может изменять пароль пользователя.
    Пользователь должен использовать функцию восстановления пароля.
    """
    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        return user


class UserCreateForm(forms.ModelForm):
    """Форма для создания нового пользователя."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Минимум 8 символов'}),
        label='Пароль',
        min_length=8
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен быть минимум 8 символов.')
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class ProductForm(forms.ModelForm):
    """Форма для редактирования товара."""
    class Meta:
        model = Product
        fields = ['category', 'article', 'name', 'slug', 'description', 'price', 
                  'image', 'stock', 'delivery_days', 'available']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'delivery_days': forms.TextInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryForm(forms.ModelForm):
    """Форма для редактирования категории."""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
