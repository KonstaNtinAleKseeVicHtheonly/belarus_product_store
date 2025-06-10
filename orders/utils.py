from django.forms import ValidationError
from .models import UserOrders, OrderItem
from carts.models import UserCart
from django.db import transaction
from django.contrib import messages


def save_orders_and_changes(request, form):
    '''Метод принмает request и form из метода form_valid в контроллере OrderCreateView содержит  алгоримт создания заказа в бд, всех необх проверок и изменении общего количества товаров на складе
    + сохраннение инфы  OrderItems для учета статистики'''

    with transaction.atomic(): # что бы не было грязного чтения
                cart_items = UserCart.objects.filter(user=request.user) # все товары из корзины юзера для сохранения в ORderItem Длч статистики
                if cart_items.exists():
                    final_order = UserOrders.objects.create(user=request.user, 
                                                            phone_number = form.cleaned_data['phone_number'],
                                                            requires_delivery = form.cleaned_data['requires_delivery'],
                                                            delivery_adress = form.cleaned_data['delivery_address'],
                                                            payment_type = form.cleaned_data['payment_type'],
                                                            email = form.cleaned_data['email'],
                                                            status = 1) # создаем заказ для юзера
                    for item in cart_items:
                        
                        if item.product.quantity < item.quantity:# хвтаит ои товара со склада
                            messages.warning(request,f"Товара{item.product.name} нет на складе")
                            raise ValidationError(f"Недостаточно товара {item.product.name} на складе , всего осталось {item.product.quantity}")
                        order_for_statictic  = OrderItem.objects.create(order=final_order,
                                                                        product=item.product,
                                                                        price = item.product.calculate_sell_price(),
                                                                        name = item.product.name,
                                                                        created_timestamp = item.created_timestamp,
                                                                        quantity = item.quantity) # сохрянею инфу для статистика в OrderItem
                        item.product.quantity -= item.quantity
                        item.product.save() # изменяем количество товара на складе

                    # form.instance.status = 1 # меняем статус заказа
                    cart_items.delete() # после оформления заказа очищаем корзину юзера (после прохожления цикла for item)
                    messages.success(request,f"Поздравляю {request.user.username}.Ваш заказ оформлен")
                else: 
                      raise ValidationError("У данного юзера нет корзин с товарами (файл order.utils.py)")