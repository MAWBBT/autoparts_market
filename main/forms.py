from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


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
