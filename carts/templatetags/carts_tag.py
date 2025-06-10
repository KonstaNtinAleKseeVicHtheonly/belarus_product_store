from django import template
from carts.models import UserCart
from carts.utils import get_user_carts

register = template.Library()# регистрируем данный тег в проекте

@register.simple_tag()
def user_carts(request):
    '''Кастомный тег, показывает всю корзину товаров данного пользователя'''
    return get_user_carts(request)
