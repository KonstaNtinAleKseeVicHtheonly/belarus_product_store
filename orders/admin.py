from django.contrib import admin
from .models import UserOrders, OrderItem

# Register your models here.
class OrderItemTabularAdmin(admin.TabularInline):
    '''для наглядного отображения инфы о заказах из корзины пользователей, прикручивается к UserOrderAdmin'''
    model = OrderItem
    fields = ('product', 'name', 'price', 'quantity' ) 
    search_fields = ('product', 'name')
    extra = 1

class OrderTabularAdmin(admin.TabularInline):
    '''Для наглядного отображения инфы о товарах в админ панели у пользователей, прикурчивается к модели StoreUser в приложении store_users'''
    model = UserOrders
    fields = ['user','created_timestamp','status','email',('payment_type','delivery_adress', 'requires_delivery')]
    search_fields = ['user', 'created_timestamp']
    readonly_fields = ['created_timestamp']
    extra = 1

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    '''панель статистики заказов за все время'''
    list_display = ['get_order_id','created_timestamp', 'name','price','quantity']
    fields = ['name','product_price','quantity','product','most_sold_product','least_sold_product']
    readonly_fields = ['name','price','quantity','product_price','most_sold_product','least_sold_product']
    ordering = ['created_timestamp','price','name']
    search_fields = ['created_timestamp','price','name']


    def get_order_id(self,obj):
        '''доп метод, что бы отображались заказаы orderitem, даже если мы удалили связанные с ними заказаы userorder'''
        if obj.order:
            return obj.order.id
        return 'DELETED'

@admin.register(UserOrders)
class UserOrderAdmin(admin.ModelAdmin):
    '''админ панель отображает заказы пользователей'''
    list_display = ['id','user','created_timestamp','status']
    fields = ['id','user','created_timestamp','status','email',('payment_type','delivery_adress', 'requires_delivery')]
    readonly_fields = ['id','user','created_timestamp','email','phone_number','payment_type']
    list_filter = ['created_timestamp','user','payment_type','phone_number']
    search_fields = ['user']
    ordering = ['created_timestamp','user']
    inlines = [OrderItemTabularAdmin]
     