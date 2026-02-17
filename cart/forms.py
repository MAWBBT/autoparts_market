from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, label='ФИО получателя')
    phone = forms.CharField(max_length=20, label='Телефон')
    email = forms.EmailField(label='Email')
    city = forms.CharField(max_length=100, label='Город')
    address = forms.CharField(max_length=300, label='Улица, дом, квартира')
    postal_code = forms.CharField(max_length=20, label='Индекс', required=False)
    PAYMENT_CHOICES = [
        ('card_online', 'Карта онлайн'),
        ('cash', 'Наличные при получении'),
        ('card_receive', 'Картой при получении'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, label='Способ оплаты')
    DELIVERY_CHOICES = [
        ('courier', 'Курьером'),
        ('pickup', 'Самовывоз'),
    ]
    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, label='Способ доставки')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Комментарий', required=False)
