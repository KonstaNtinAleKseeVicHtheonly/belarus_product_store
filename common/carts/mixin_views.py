from django.urls import reverse
from carts.models import UserCart
from django.template.loader import render_to_string
from carts.utils import get_user_carts

class CartMixin():
    '''миксин для расширения view в контроллерах приложения carts для взаимодействия с ajax'''

    def get_cart(self,request,product=None,cart_id=None):
        '''Метод для получения корзины по указанному продукту '''

        if request.user.is_authenticated:
            query_info = {'user' : request.user}
        else:
            query_info = {'session_key' : request.session.session_key}
        if product:
            query_info['product'] = product
        if cart_id:
            query_info['id'] = cart_id
        try:
            return UserCart.objects.filter(**query_info).first()
        except Exception as err:
            return f"Произошла ошибка при взаимодействии с корзиной пользователя (в миксине CartMixin){err}"


        
    def render_cart(self,request):
        '''Метод для преобразовани инфы шаблона(для перерисовки в ajax) в строку'''
        context = {'carts':get_user_carts(request) }
        referer = request.META.get('HTTP_REFERER')

        if reverse('all_orders:create_order') in referer: # что бы при имзенении коризны в заказае, кнопка 'оформить' не выскакивала
            context['order'] = True
        return  render_to_string(
            'carts/includes/included_cart.html', 
            context=context, 
            request=request)
    