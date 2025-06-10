from django.db import models
# мпорт моделей
from products.models import Product
from store_users.models import StoreUser


# Create your models here.
class CartQuerySet(models.QuerySet):
    '''Вспомогательынй класс для класса Cart, расширяющий функционал базвого менеджжера, вычисляет общую цену товаров и их количество,
    этот класс будет срабатывать, когда мы будем обращаться к QuerySet у класса Cart(Cart.objects.all() например)'''
     
    def general_sum(self):
        '''Возвращает итоговую сумму всех товаров во всех корзинах текущего пользователя'''
        return sum(cart.product_price_in_cart() for cart in self)

    def general_quantity(self):
        '''Возвращает общее количество товаров из всех корзин'''
        if self:
             return sum(cart.quantity for cart in self)
        return 0

class UserCart(models.Model):
    '''модель корзины товаров, отображает товар, цену, количество
    так же есть метолы для расчета общей стоимости, для увеличения 
    и уменьшения количества товара.Логика корзины:для каждого товара создается отдельная корзина, 1 продукт - 1 корзина'''
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name='Продукт')
    user = models.ForeignKey(to=StoreUser, on_delete=models.CASCADE,verbose_name='Пользователь',null=True,blank=True)#если юзера нет, по умолчанию ноль(незареганнный юзер)
    quantity = models.PositiveIntegerField(verbose_name='Количество')#количество товара в корзине, инфа для пользователя
    created_timestamp = models.DateTimeField(auto_now_add=True,verbose_name='Дата добавления')
    session_key = models.CharField(max_length=32,null=True,blank=True)# уникальный ключ сессии для каждого неавторизованного бзера,
    objects = CartQuerySet.as_manager() # для связи в вспомогательным классом CartQuerySet

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username} с товаром {self.product.name} в количестве {self.quantity}"
        return f"Корзина анонимного пользователя с товаром {self.product.name} в количестве {self.quantity}"
    
    class Meta:
        db_table = 'Cart'# имя таблицы в субд(postgre)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def product_price_in_cart(self):
        '''Возвращает сумму товара в корзине, в зависимости от количества и скидки'''
        return float(self.product.calculate_sell_price()) * float(self.quantity) # все через float суммировать иначе конфликт decimal и float
