from django.db import models
# импорт моделей проекта
from store_users.models import StoreUser
from carts.models import UserCart
from products.models import Product
# доп функциоанл
from django.db.models import Sum
# Create your models here.

class UserOrders(models.Model):
    '''модель отображающая заказы пользователя, отображающая основную инфу о товаре, статуст и прочее'''
    CREATED = 0
    PAID = 1
    CANCELLED = 2
    ON_WAY = 3
    DELIVERED = 4
    STATUS_DESCRIPTION = [(CREATED,'Создан'), (PAID,'Оплачен'),(CANCELLED,'Отменен'),(ON_WAY, 'В пути'), (DELIVERED, 'Доставлен')]

    
    user = models.ForeignKey(to=StoreUser, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    phone_number = models.CharField(max_length=20, verbose_name='номер телефона')
    requires_delivery = models.BooleanField(default=False, verbose_name='Требуется доставка')
    delivery_adress = models.CharField(max_length=70,verbose_name='адрес доставки')
    payment_type = models.BooleanField(default=False,verbose_name='способ оплаты')
    email = models.EmailField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_DESCRIPTION, default=CREATED, verbose_name='Статус заказа')
    created_timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')
    
    class Meta:
        db_table = 'user_orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'  

    def __str__(self):
        return f"Заказ № {self.pk} пользователя {self.user}"
    
class OrderItemQueryset(models.QuerySet):
    '''доп класс для OrderItem, расшираяющий функционал менеджера objects'''
    def total_price(self):
        '''Расчитает полную стоимость товаров в корзине, через метод расчета цены, прописаный в UserCart,
        который в свою очередь вызывет метод расчета цены продукта в классе Product'''

        if self:
            return sum(cart.product_price_in_cart() for cart in self)
        return 0
    
    def total_quantity(self):
        '''Метод расчитает общее количество проданных товаров'''
        if self:
            return sum(cart.quantity for cart in self)
        return 0
    
class OrderItem(models.Model):
    '''Таблица с оформленными заказами для ведения статистики'''
    order = models.ForeignKey(to=UserOrders, on_delete=models.SET_NULL, null=True,blank=True,related_name='order_items')
    product = models.ForeignKey(to=Product, on_delete=models.SET_DEFAULT, verbose_name='Продукт', default=1)
    price = models.IntegerField(verbose_name='цена')
    name = models.CharField(max_length=150, verbose_name='Название')
    created_timestamp = models.DateTimeField(auto_now_add=True,verbose_name='Дата покупки')
    quantity = models.PositiveIntegerField(default=0, verbose_name='количество товара')
    objects  = OrderItemQueryset.as_manager() # связь с классом расширяяющим функционал pbjects у OrderItem

    class Meta:
        db_table = 'orderitem'
        verbose_name = 'Проданный товар'
        verbose_name_plural = 'Проданные товары'

    def __str__(self):
        if self.order:# переопределил метод, т.к при удалении заказа из USerOrder, ошибка в OrderItem возникала связанная с отсутсвием pk
            return f"ЗАказ № {self.order.pk} С товаром {self.product.name} | {self.quantity} шт."
        return 'DELETED'
    
    def product_price(self):
        '''Вернет сумму определенного проданного товара'''
        return (self.product.calculate_sell_price() * self.quantity)
    
    def make_statistic(self,sign:str):
        '''Делает статистку о наиболее и наименнее продаваемом товара, в зависимотси от sign'''
        if not isinstance(sign,str): # валидация входных данных
            raise ValueError('Пожалуйста введите строковое значение most или least')
        sign = sign.lower().strip()
        if sign in ('most', 'least'):
            statistic = (
                    OrderItem.objects
                    .values('product__name')  # Группируем по названию товара
                    .annotate(total_sold=Sum('quantity')))  # Суммируем количество
            if sign == 'most':
                return statistic.order_by('-total_sold').first() # сортировка по убыванию беру первый эелемент
            return statistic.order_by('total_sold').first() # сортировка по возрастанию беру первый эелемент
        return "Пожалуйста введите 'most' или 'least'"

    def most_sold_product(self):
        current_statistic = self.make_statistic('most')
        if not current_statistic:
            return 'нет данных о продажах'
        return f"Самый продаваемый: {current_statistic['product__name']} ({current_statistic['total_sold']} шт.)"
    
    
    def least_sold_product(self):
        current_statistic = self.make_statistic('least')
        if not current_statistic:
            return 'нет данных о продажах'
        return f"Наименее продаваемый: {current_statistic['product__name']} ({current_statistic['total_sold']} шт.)"
        

