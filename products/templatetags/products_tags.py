from products.models import Product, ProductCategory
from django import template
from django.utils.http import urlencode

register = template.Library()# регистратор тегов в системе

@register.simple_tag()
def tag_categories():
    ...

@register.simple_tag(takes_context=True)# регистрируем тег для сохранения фильтрации при пагинации
def change_params(context, **kwargs): # все переменные контекста в переменной context
    '''Что бы при переходе на другую страницу, фильтрация не сбрасывалась'''
    query = context['request'].GET.dict() # формируем словарь из данных с request но уже с примененной фильтрацией
    query.update(kwargs) # дополняем context инфо о продуктах с примененной фильтрацией, передавая инфу из kwargs

    return urlencode(query) # возращает вместо словаря строку, которую используем в url адресе