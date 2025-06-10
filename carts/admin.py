from django.contrib import admin
from .models import UserCart


# Register your models here.
class UserCartTabAdmin(admin.TabularInline):
    '''Модель покажет корзины текущего б=юзера'''
    model = UserCart # модель привязки
    fields = ["product", "quantity", "created_timestamp"]
    search_fields = ["product", "quantity", "created_timestamp"]
    readonly_fields = ["created_timestamp"]
    extra = 1

@admin.register(UserCart)
class UserCartAdmin(admin.ModelAdmin):
    '''Админка для корзины пользователей'''
    list_display = ['reflect_user','reflect_product','quantity','created_timestamp']
    list_filter = ['user__username']

    search_fields = ['user']
    ordering = ['user']
    
    def reflect_user(self,obj):
        '''метод отображает имя юзера если есть или анонима'''
        if obj.user:
            return f"Корзина пользователя {obj.user}"
        return "Картина анонимного пользователя"
    def reflect_product(self, obj):
        '''покажет имя продукта, что бы метод str не срабатывал в product с ненужнйо инфой'''

        return str(obj.product.name)

