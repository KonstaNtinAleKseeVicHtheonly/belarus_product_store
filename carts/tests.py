from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware # для теста сессий
from django.urls import reverse
# тест моделей
from .models import UserCart
from store_users.models import StoreUser
from products.models import Product, ProductCategory
#контроллеры
from .views import CartAddView, CartChangeView, CartRemoveView
# логер
import logging
from logger.project_logger import configure_logging
# доп утилиты
import json


test_logger = logging.getLogger(__name__)
configure_logging(level='INFO')


# Create your tests here.

class CartAddTest(TestCase):
    '''тест контроллера CartAddView'''
    def setUp(self):
        self.path = reverse('all_carts:cart_add')
        self.factory = RequestFactory()
        self.test_category = ProductCategory.objects.create(name='test_category', slug='test-category')
        self.test_product = Product.objects.create(name='test_product',slug='test-product', category=self.test_category,price=3,discount=10,weight=30, image='edas')
        self.test_user = StoreUser.objects.create_user(username='testuser',first_name='test_name',last_name='test_last_name',
                                                 password='complexpassword123',email='test@example.com')
        self.test_cart = UserCart.objects.create(product=self.test_product,user=self.test_user,quantity=1)
        self.view = CartAddView

    def _adding_session(self, request):
        midleware = SessionMiddleware(lambda req:None)
        midleware.process_request(request)
        request.session.create()

    def test_adding_wrong_product(self):
        '''проверка если доавить несущестсуюущий товар'''
        request = self.factory.post(self.path, data={'product_id' : 228})
        self._adding_session(request)
        request.user = self.test_user # автризированный юзер
        response = self.view.as_view()(request)

        data = json.loads(response.content.decode(encoding='utf-8'))
        test_logger.info(f"инфа об ответе в add_wrong_product {data}")

        self.assertEqual(response.status_code,400)
        self.assertEqual(data['status'], 'error')
        self.assertIn('No Product matches the given query.',data['message'] )

    def test_add_product_anonymous_user_new_cart_item(self):
        """Тест: анонимный пользователь добавляет новый товар в корзину, создаётся корзина с сессионным ключом."""
        request = self.factory.post(self.path, data={'product_id': self.test_product.id})
        self._adding_session(request)
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()  # Анонимный пользователь

        response = self.view.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))

        test_logger.info(f"инфа о data в add_product {data}")
        self.assertIsNotNone(request.session.session_key)

    def test_error_when_product_id_not_provided(self):
        """Тест: если в запросе не передан ID товара, возвращается ошибка."""
        request = self.factory.post(self.path, data={})
        self._adding_session(request)
        request.user = self.test_user

        response = self.view.as_view()(request)
        data =  json.loads(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Не указан ID товара')






class CartChangeTest(TestCase):
    '''тест контррллера CartCahngeView'''

    def setUp(self):
        self.path = reverse('all_carts:cart_change')
        self.factory = RequestFactory()
        self.test_category = ProductCategory.objects.create(name='test_category', slug='test-category')
        self.test_product = Product.objects.create(name='test_product',slug='test-product', category=self.test_category,price=3,discount=10,weight=30, image='edas')
        self.test_user = StoreUser.objects.create_user(username='testuser',first_name='test_name',last_name='test_last_name',
                                                    password='complexpassword123',email='test@example.com')
        self.test_cart = UserCart.objects.create(product=self.test_product,user=self.test_user,quantity=1)
        self.view = CartChangeView

    def _adding_session(self, request):
        """Добавляем сессию к запросу и создаём session_key."""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.create()

    def test_invalid_change_cart(self):
        '''проверка попытки ввести невалидные данные'''
        request = self.factory.post(self.path, data = {'cart_id':self.test_cart.id,
                                                        'quantity' : '' })
        self._adding_session(request)
        request.user = self.test_user # авторизированный юзер

        response = self.view.as_view()(request)
        data = json.loads(response.content.decode('utf-8'))
        test_logger.info(f'инфа о =б ответе в changecart{data}')

        self.assertEqual(response.status_code,400)
        self.assertEqual(data['status'], 'error')
        self.assertIn("Field 'quantity' expected a number but got ''.", data['message'])

