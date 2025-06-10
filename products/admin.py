from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Product, ProductCategory


# Register your models here.
@admin.register(ProductCategory)
class ProductCategoryAdmin(DraggableMPTTAdmin):
    ''''админка для категорий товаров'''
    mptt_level_indent = 30 # отступ в древовидной структуре
    list_display = ('tree_actions', 'indented_title')
    list_display_links = ('indented_title',)
    search_fields = ['name', 'products__name']
    prepopulated_fields = {'slug': ('name',)} # что бы slug имена автоматически заполнялисль в админке, slug-поле заполнения,name-из какого поля брать инфу


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    '''админка для товаров'''

    list_display = ('id', 'name', 'price', 'discount','discount_price','category','quantity','is_active','delivered')
    fields = [ 'name', 'category',('price','discount','discount_price'),'image','slug','description','quantity','is_active', 'energy_value','delivered']  # поля отодражающие позиции опред товара
    list_editable = ['name', 'price', 'discount','category','quantity','is_active','delivered']
    search_fields = ['name', 'category__name'] # category__name т.к по foreing key- mppt не поддерживает поиск
    list_filter = ['category__name','price','quantity',]
    # не работает как надо, переделать логику методов
    ordering = ['name','price']  # сортировка по цене, количеству
    prepopulated_fields = {'slug': ('name',)} # что бы slug имена автоматически заполнялисль в админке
