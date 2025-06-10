from django import forms
from .models import UserOrders

class OrderForm(forms.ModelForm):
    '''форма для зшаблона страницы с заказами юзера с завязкой на бэкенд'''

    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class' : "form-control",
        'placeholder' : 'Введите имя'}))
    second_name = forms.CharField(widget=forms.TextInput(attrs={
        'class' : "form-control",
        'placeholder' : 'Введите фамилию'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : '+7 (XXX) XXX-XX-XX'
                                        }),initial='+7')
    email  = forms.EmailField(widget=forms.EmailInput(attrs={
        'class' : 'form-control',
        'placeholder' : "you@example.com"}))
    requires_delivery = forms.ChoiceField(widget=forms.RadioSelect(),choices=
                                         [('0', False),
                                          ('1', True)], initial='0',help_text='требует доставки')
    delivery_address = forms.CharField(required=False,widget=forms.Textarea(attrs={
            'class' : 'form-control',
            'id' : 'delivery-address',
            'rows' : 2,
            'placeholder' : 'Пример адреса: Россия, Москва, ул. Мира, дом 6'
                                        }))
    payment_type = forms.ChoiceField(widget=forms.RadioSelect(),choices=
                                         [('0', 'Оплата по карте'),
                                          ('1', 'Наличка')],
                                          initial='0')
    
    class Meta:
        model= UserOrders
        fields = ['first_name', 'second_name','email','requires_delivery', 'delivery_address','payment_type']

class OrderFormAlternative(forms.Form):
    '''Доп форма, не привязанная к ModelForm(без MEta класса), т.к может пригодиться кастомная валидаци. Завязка на фронтенд'''

    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()
    requires_delivery = forms.ChoiceField()
    delivery_address = forms.CharField(required=False) # необязательно
    payment_type = forms.ChoiceField()
    email = forms.CharField()
    address = forms.CharField()

    class Meta:
        model= UserOrders
        fields = {'first_name', 'last_name','phone_number', 'requires_delivery', 'delivery_address','payment_type','email','address'}



    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class' : "form-control",
        'placeholder' : 'Введите имя'}))
    second_name = forms.CharField(widget=forms.TextInput(attrs={
        'class' : "form-control",
        'placeholder' : 'Введите фамилию'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Введите номер телефона'
                                        }))
    email  = forms.EmailField(widget=forms.EmailInput(attrs={
        'class' : 'form-control',
        'placeholder' : "you@example.com"}))
    adress = forms.CharField(widget=forms.TextInput(attrs={
        'class' : "form-control",
        'placeholder' : 'Пример адреса: Россия, Москва, ул. Мира, дом 6'}))
    requires_delivery = forms.ChoiceField(widget=forms.RadioSelect(),choices=
                                         [('0', False),
                                          ('1', True)])
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={
            'class' : 'form-control',
            'id' : 'delivery-address',
            'rows' : 2,
            'placeholder' : 'Введите адрес доставки'
                                        }))
    payment_type = forms.ChoiceField(widget=forms.RadioSelect(),choices=
                                         [('0', False),
                                          ('1', True)],
                                          initial='card')
    