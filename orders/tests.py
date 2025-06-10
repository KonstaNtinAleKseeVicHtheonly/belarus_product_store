from django.test import TestCase, RequestFactory 
from django.contrib.messages.storage.fallback import FallbackStorage # для костыля 
from django.urls import reverse, reverse_lazy # для тестирвоания url
#импорт моделей
from .models import UserOrders
from products.models import Product, ProductCategory
from store_users.models import StoreUser
from django.contrib.auth.models import AnonymousUser # симуляция действий анонимного пользователя
#импорт формы
from .forms import OrderForm
# контроллеры
from .views import OrderCreateView

# логгирование
import logging
from logger.project_logger import configure_logging
# установить coverage покрытие процент покрытия тестами
# прочие приблуды 
from django.core.exceptions import ObjectDoesNotExist
test_logger = logging.getLogger(__name__)

configure_logging(level='INFO')

class TestOrderCreateView(TestCase):
    '''тестирование контроллера OrderCreateVIew'''
    
    def setUp(self):
        self.path = reverse('all_orders:create_order')
        self.factory = RequestFactory()
        self.test_category = ProductCategory.objects.create(name='test_category', slug='test-category')
        self.test_product = Product.objects.create(name='test_product',slug='test-product', category=self.test_category,price=3,discount=10,weight=30, image='edas')
        self.test_user = StoreUser.objects.create_user(username='testuser',first_name='test_name',last_name='test_last_name',
                                                 password='complexpassword123',email='test@example.com')
        self.test_order = UserOrders.objects.create(user=self.test_user,
                                                    phone_number='88005553535',
                                                    delivery_adress='Кукуево',
                                                    email='testmail@inbox.ru')

    def test_correct_template(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/create_order.html')

    def test_context_data(self):
        self.client.force_login(self.test_user)
        response = self.client.get(self.path)
        self.assertIn('form', response.context.keys())
        self.assertIsInstance(response.context['form'], OrderForm)
        self.assertTrue('order')

    def test_successful_order_creation(self):
        '''тест для проверки создания заказа'''
        valid_data = {'username': 'testuser',
            'first_name' : 'test_name',
            'second_name' : 'test_last_name',
            'phone_number' : '88005553535',
            'email' : 'example@inbox.cum',
            'requires_delivery' : '1' ,
            'delivery_address' : 'Бутово',
            'payment_type' : '1'
        }
        self.client.force_login(self.test_user)
        
        response = self.client.post(self.path, valid_data)
        # провера редиректа при валидных данных
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('all_users:current_profile'))
        # проверка создания заказа
        self.assertEqual(UserOrders.objects.count(), 1)
        self.assertEqual(UserOrders.objects.first().user, self.test_user)

    def test_invalid_order_data(self):
        '''проверка ввода невалидных данных при создании заказа'''
        invalid_data = {'username': '',
            'email': 'blablabla',
            'first_name' : 'test_name',
            'second_name' : 'test_last_name',
            'requires_delivery' : '' ,
            'payment_type' : ''
        }
        self.client.force_login(self.test_user)
        response = self.client.post(self.path, invalid_data)
        test_logger.info(f"Инфа неправильного заказа {list(response.context['messages'])}")
        self.assertEqual(response.status_code, 200)
        warning_message = list(response.context['messages'])
        self.assertIn('Пожалуйста введите данные для оформления заказа', str(warning_message[0]))
        self.assertEqual(UserOrders.objects.count(), 1) # тест что количество заказов не изменилось




    def test_requires_login(self):
        '''Проверка, что анонимный юзер не может создавать заказа без авторизации'''
        request = self.factory.get(self.path)
        request.user = AnonymousUser() # тип анонимный юзер входит
        response = OrderCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302) # редирект на страницу входа
