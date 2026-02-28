from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm as BasePasswordChangeForm
from .models import UserProfile

User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя."""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
        required=True,
    )
    full_name = forms.CharField(
        label='Полное имя',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
        required=True,
    )

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
        }
        labels = {
            'phone': 'Телефон',
        }
        help_texts = {
            'phone': 'Необязательное поле. Можно оставить пустым.',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['full_name'].initial = self.user.full_name or (self.instance.full_name if self.instance.pk else '')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Проверяем, что email уникален (кроме текущего пользователя)
            if User.objects.filter(email=email).exclude(id=self.user.id).exists():
                raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            # Обновляем email и full_name в модели User
            self.user.email = self.cleaned_data['email']
            self.user.full_name = self.cleaned_data['full_name']
            if commit:
                self.user.save()
                profile.save()
        return profile


class PasswordChangeForm(BasePasswordChangeForm):
    """Форма для изменения пароля пользователя в профиле."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Улучшаем стили полей
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите текущий пароль'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Минимум 8 символов'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите новый пароль'
        })
        # Улучшаем метки
        self.fields['old_password'].label = 'Текущий пароль'
        self.fields['new_password1'].label = 'Новый пароль'
        self.fields['new_password2'].label = 'Подтверждение нового пароля'
        
        # Добавляем help text для нового пароля
        if self.fields['new_password1'].help_text:
            self.fields['new_password1'].help_text = 'Минимум 8 символов. Рекомендуется использовать комбинацию букв, цифр и символов.'


class RegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        label='ФИО',
        widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
    )
    phone = forms.CharField(
        max_length=20,
        label='Телефон',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
    )
    agree_terms = forms.BooleanField(
        label='Я согласен с пользовательским соглашением и политикой конфиденциальности',
        required=True,
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # OGR из ЛР №7: символ @
        if email and '@' not in email:
            raise forms.ValidationError('Email должен содержать символ @')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1') or ''
        # OGR из ЛР №7: минимум 8 символов
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен быть минимум 8 символов.')
        return password

    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            raise forms.ValidationError({'password2': 'Пароли не совпадают.'})
        return data

    def save(self):
        email = self.cleaned_data['email']
        user = User.objects.create_user(email=email, password=self.cleaned_data['password1'], full_name=self.cleaned_data['full_name'])
        UserProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['full_name'],
            phone=self.cleaned_data.get('phone', ''),
        )
        return user
