from django.shortcuts import  get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
# импорт классов представлений
from django.views import View
#импорт моделей
from carts.models import UserCart
from products.models import Product
# импорт кастомных миксинов
from common.carts.mixin_views import CartMixin
# вспомогательный инструменты и утилиты
from .utils import get_user_carts
from django.contrib import  messages
import logging
from logger.project_logger import configure_logging
# Create your views here.

logger = logging.getLogger(__name__)
configure_logging(level='INFO')

class CartAddView(CartMixin,View):
    '''Класс для добавления товара в корзину + увеличения его количества в корзине.Прикручен ajax с страницы, что бы она не обнавлялась при каждом изменении'''

    def post(self, request):
            
        try:
            product_id = request.POST.get('product-id') or request.POST.get('product_id')
            if not product_id:# если такого id нет в бд
                return JsonResponse({'status': 'error', 'message': 'Не указан ID товара'}, status=400)
            product = get_object_or_404(Product, id=product_id) # находим товар по id
            current_cart = self.get_cart(request, product=product)

            if current_cart:
                current_cart.quantity +=1
            else:
                if request.user.is_authenticated:
                    UserCart.objects.create(user=request.user,product=product, quantity=1)
                else: 
                    UserCart.objects.create(session_key=request.session.session_key,product=product,quantity=1)
            response_data = {
                'status': 'success',
                'message': f'Товар {product.name} добавлен в корзину',
                'cart_items_html': self.render_cart(request),
            }
            return JsonResponse(response_data)
        except Exception as e:
            logger.error(f"Ошибка добавления в корзину: {str(e)} {product_id}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)


class CartChangeView(CartMixin,View):
    '''Контроллер для измения количества товара в корзине при нажатии на кнопки'''

    def post(self,request):
        try:
            cart_id = request.POST.get('cart_id')
            change_cart_quantity = request.POST.get('quantity') # количество в коризну для изменения
            current_cart = self.get_cart(request,cart_id=cart_id)

            current_cart.quantity = change_cart_quantity # текущее количество товаров после изменения
            current_cart.save()


            response_data = { 'message':f"Количество товара {current_cart.product.name} изменено",
                        'cart_items_html' : self.render_cart(request),
                        'quantity' : current_cart.quantity}
            logger.info(f"Количество товара {current_cart.product.name} изменено")
            return JsonResponse(response_data)
        except Exception as err:
            return JsonResponse({
                'status': 'error',
                'message': str(err)
            }, status=400)

class CartRemoveView(CartMixin,View):
    '''контроллер для удаления товаров из корзины'''

    def post(self, request):
        try:
            cart_id = request.POST.get('cart_id')
            current_cart = self.get_cart(request,cart_id=cart_id) # находим корзину которую хотят удлаиь по id
            
            quantity = current_cart.quantity

            current_cart.delete()


            response_data = {'message' : f"Товар {current_cart.product.name} успешно удален из корзины",
                        'cart_items_html' : self.render_cart(request),
                        'quantity_deleted' : quantity}
            
            return JsonResponse(response_data)
        except Exception as err:
            return JsonResponse({
                'status': 'error',
                'message': str(err)
            }, status=400)
        
# контроллеры на основе функиий с прикруткой ajax ручным алгоритмом добавки и т.д (на случай если контроллеры на основе классов перестанут работать)

# def cart_add(request):
#     '''метод для добавления товара в корзину + увеличения его количества в корзине'''
#     try:
#         # 1. Получаем product-id 
#         product_id = request.POST.get('product-id') or request.POST.get('product_id')
#         if not product_id:# если такого id нет в бд
#             return JsonResponse({'status': 'error', 'message': 'Не указан ID товара'}, status=400)
#         # 2. Находим товар
#         product = get_object_or_404(Product, id=product_id)
#         if request.user.is_authenticated:
#             # 3. Ищем существующую корзину (используем get_or_create для атомарности)
#             cart_item, created = UserCart.objects.get_or_create(
#                 user=request.user,
#                 product=product,
#                 defaults={'quantity': 1} # если товаоа не было такого, созлаем его в количестве 1 шт
#             )
#         else:# если юзер не авторизован, то определяем корзину по ключу сессии
#             cart_item, created = UserCart.objects.get_or_create(
#                 session_key=request.session.session_key,
#                 product=product,
#                 defaults={'quantity': 1}
#             )# если товаоа не было такого, созлаем его в количестве 1 шт
#         if not created:# если такой товар уже был
#             cart_item.quantity += 1
#             cart_item.save()
#         # 5. Формируем ответ
#         cart_items_html = render_to_string(
#             'carts/includes/included_cart.html', 
#             {'carts': get_user_carts(request)}, 
#             request=request
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'message': f'Товар {product.name} добавлен в корзину',
#             'cart_items_html': cart_items_html,
#             'new_quantity': cart_item.quantity,
#             'created': created
#         })
#     except Exception as e:
#         logger.error(f"Ошибка добавления в корзину: {str(e)} {product_id}")
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=400)


    # вариант без ajax
    # plus_product = Product.objects.get(slug=product_slug)# есть ли такой товар вообще в базе
    # current_cart = UserCart.objects.filter(user=request.user,product=plus_product)
    # if current_cart.exists():# если такой товар уже был, его количество нужно увеличить на один
    #     user_cart = current_cart.first()
    #     user_cart.quantity +=1
    #     user_cart.save()
    #     messages.success(request,f"Теперь у вас {user_cart.quantity} шт. {plus_product.name}")
    # else:# иначе добавим этот товар в корзину в количестве 1 шт.
    #     messages.success(request,f"{plus_product.name} успешно добавлен в корзину")
    #     UserCart.objects.create(user=request.user,product=plus_product,quantity=1)
    # return HttpResponseRedirect(request.META['HTTP_REFERER']) # поосле изменения количества товара возвращаем юзера на туже страницу где он и был

# def cart_change(request):
#     '''Контроллер для измения количества товара в корзине при нажатии на кнопки'''
#     cart_id = request.POST.get('cart_id')
#     change_cart_quantity = request.POST.get('quantity') # количество в коризну для изменения
#     current_cart = UserCart.objects.get(id=cart_id)# текущая корзину юзеа по данному id
#     logger.info(f"инфа из post запроса на изменение товаров в корзине {request.POST}")

#     current_cart.quantity = change_cart_quantity# изменяем текущее количество товаров данной корзины
#     current_cart.save()

#     all_users_cart =get_user_carts(request) # берем все корзины юзера уже полсе изменения для перерисовки на странице

#     cart_items_html = render_to_string('carts/includes/included_cart.html', {'cart' : all_users_cart}, request=request)
#     response_data = { 'message':f"Количество товара {current_cart.product.name} изменено",
#                      'cart_items_html' : cart_items_html,
#                      'quantity' : current_cart.quantity}    
    
#     return JsonResponse(response_data)

    # # алгоритм уменьшения единиц товара без ajax
    # if minus_cart.exists():
    #     minus_product = minus_cart.first()
    #     if minus_product.quantity > 1:# уменьшаем количество товаров
    #         minus_product.quantity -= 1
    #         minus_product.save()
    #     else:
    #         minus_product.delete()# удаляем данный товар из корзиный
            
    # return HttpResponseRedirect(request.META['HTTP_REFERER']) 

# def cart_remove(request):

#     logger.warning(f"Вот инфа для  удаления {request.POST}")
#     cart_id = request.POST.get('cart_id') # находим текущую корзину по id
#     if not cart_id:
#         logger.warning(f"Ошибка с словарем POST запроса {request.POST}")
#         raise ValueError('В post запросе другой ключ словаря к id')
#     try:
#         if request.user.is_authenticated:
#             current_cart = UserCart.objects.get(id=cart_id)
#         else:
#             current_cart = UserCart.objects.get(id=cart_id,session_key=request.session.session_key) # что бы найти корзину невториз. юзера
#     except Exception as error:
#         logger.error(f"В БД нет корзины с id {cart_id}, {error}")
#     else:    
#         current_cart.delete()
#         logger.warning(f"продукт {current_cart.product.name} успешно удален")

#     if current_cart.quantity > 0: # что бы грамотно работала отрисовка товаров в корзине полсе удаления, иначе булет отрицательный показатель корзины
#         quantity = current_cart.quantity

#     user_cart = get_user_carts(request) # возвращаем обновленную корзину с удаленнымми товарами
#     cart_items_html = render_to_string('carts/includes/included_cart.html', {'cart':user_cart}, request=request)
#     response_data = {'message' : f"Товар {current_cart.product.name} успешно удален из корзины",
#                      'cart_items_html' : cart_items_html,
#                      'quantity_deleted' : quantity}
#     return JsonResponse(response_data)



    # # алгоритм уменьшения единиц товара
    # if minus_cart.exists():
    #     minus_product = minus_cart.first()
    #     if minus_product.quantity > 1:# уменьшаем количество товаров
    #         minus_product.quantity -= 1
    #         minus_product.save()
    #     else:
    #         minus_product.delete()# удаляем данный товар из корзиный
            
    # return HttpResponseRedirect(request.META['HTTP_REFERER']) 