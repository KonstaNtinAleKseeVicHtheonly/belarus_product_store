from django.contrib import admin
from .models import StoreUser
from django.db.models import QuerySet
from carts.admin import UserCartTabAdmin
from orders.admin import OrderTabularAdmin



# Register your models here.
@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    list_display = ['username','first_name','last_name','is_active','is_staff','is_superuser']
    search_fields = ['username', 'first_name','last_name']
    actions = ['admin_deprivation', 'staff_deprivation']
    list_filter = ['is_superuser','is_staff']
    inlines = (UserCartTabAdmin,OrderTabularAdmin)# поле, показывающее корзины данного юзера

    @admin.action(description='Лишение полномочий админа')
    def admin_deprivation(self,request,queryset:QuerySet):
        queryset.update(is_superuser=False)
        self.message_user(request, 'Пользователь лишен полночочий админа')

    @admin.action(description='ЛИшение полномочий работника')
    def staff_deprivation(self,request, queryset:QuerySet):

        queryset.update(is_staff=False)
        self.message_user(request, 'Пользователь лишен полночочий работника')

    