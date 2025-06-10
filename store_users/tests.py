from django.test import TestCase
from django.urls import reverse, reverse_lazy # для тестирвоания url
#импорт моделей
from .models import StoreUser
from products.models import Product, ProductCategory
from carts.models import UserCart
# импорт форм приложения
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserChangeForm
# логгирование
import logging
from logger.project_logger import configure_logging
# установить coverage покрытие процент покрытия тестами
# прочие приблуды 
import json
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
test_logger = logging.getLogger(__name__)


configure_logging(level='INFO')

# Create your tests here.

class UserRegistrationTest(TestCase):
    '''Тестирование контроллера UserRegistrationView'''
    def setUp(self):
        self.path = reverse('all_users:current_registration')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name' : 'test_name',
            'last_name' : 'test_last_name',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        }# данные для регистрации
        self.invalid_data = {
            'username': 'testuser',
            'email': 'hzhzzh',
            'first_name' : 'test_name'
            } # невалидные данные чо бы не зарегался юзер

    def test_view(self):
        '''базовое тестирование контроллера на подключение и шаблон, наличие формы'''
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store_users/registration.html')
        self.assertIn('form', response.context.keys())
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

        # Проверка наличия полей формы в HTML
        self.assertContains(response, 'name="username"') 
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="last_name"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
           
    def test_successful_registration(self):
        """Проверка успешной регистрации пользователя"""
        
        # имитцация регистрации юзера
        self.assertFalse(StoreUser.objects.filter(username=self.valid_data['username']).exists())# проверка что тестового юзера не было в бд до его создания
        response = self.client.post(self.path, self.valid_data)# регаем тестового юзера с указанными данными
        # Проверка редиректа после успешной регистрации
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=reverse('all_users:current_profile'))
        # проверка, создался ли юзер в БД
        self.assertTrue(StoreUser.objects.filter(username=self.valid_data['username']).exists())

    def test_invlid_data(self):
        '''тест на случай ввод невалидных данных в форму регистрации'''

        # проверка, что юзер не создался
        response = self.client.post(self.path, self.invalid_data)
        self.assertFalse(StoreUser.objects.filter(username=self.invalid_data['username']))
        self.assertEqual(response.status_code, 200)
    
    def test_occupied_position(self):
        '''тест случая, когда пользователь с вводимыми данными уже существует'''
        previous_user = StoreUser.objects.create(username='testuser',first_name='test_name',last_name='test_last_name',
                                                 password='complexpassword123',email='test@example.com')
        self.assertEqual(len(StoreUser.objects.all()),1) # количество юзеро в бд до попытки регитстрации
        response = self.client.post(self.path, self.valid_data) # попытка регистрации юзера
        test_logger.info(f"инфа из ответа {response.context['messages']}")
        self.assertEqual(response.status_code,200) # если код 200 значит не было редиректа, тобишь  юзер уже был в бд
        self.assertEqual(len(StoreUser.objects.all()),1) # проверить что количество юзеров  бд не изменилось


        
        

class UserLoginTest(TestCase):
    '''Тестирование контроллера UserLoginView'''

    def setUp(self):
        self.path = reverse('all_users:current_login')
        self.registered_user = StoreUser.objects.create_user(username='testuser',first_name='test_name',last_name='test_last_name',
                                                 password='complexpassword123',email='test@example.com')
        self.login_data = {'username': 'testuser',
                      'password': 'complexpassword123'
                      } # данные для авторизации
        
        # тестовые данные для проверки создания корзины юзера
        test_category = ProductCategory.objects.create(name='test_category',slug='test-category')
        self.test_product = Product.objects.create(name='test_product',slug='test-product', category=test_category,price=3,discount=10,weight=30, image='edas')

    def test_base_view(self):
        '''базовое тестирование контроллера на подключениее по данному url, наличие шаблона и т.д'''
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'store_users/login.html')
        self.assertIn('form', response.context.keys())
        self.assertIsInstance(response.context['form'], UserLoginForm)

    def test_successful_login(self):
        login_data = {'username': 'testuser',
                      'password': 'complexpassword123'
                      }
        response = self.client.post(self.path,login_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response,reverse_lazy('all_users:current_profile'))
        success_message = list(get_messages(response.wsgi_request))
        test_logger.info(f"инфа из сообщения при успешной авторизации {success_message}")
        self.assertEqual(len(success_message), 1)
        self.assertIn("Добро пожаловать в свой профиль, testuser", str(success_message[0])) # сообщение об успешной авторизации
    
    def test_invalid_login(self):
        '''если введены невалидные данные'''
        invalid_login_data = {'username': 'wronguser',
                      'password': 'wrongpassword'
                      }
        response = self.client.post(self.path, invalid_login_data)
        form_response = response.context['form']
        self.assertTrue(form_response.errors) # если есть инфа об ошибке значит невалидный логин
        self.assertEqual(response.status_code, 200)
        # доп проверка на текст о невалидных данных
        self.assertContains(response, "Пожалуйста, введите правильные имя пользователя и пароль")

    def test_cart_changing_after_login(self):
        '''проверка, сохраняются ли коризны после авторизации'''
        # создаю анонимную корзину
        session = self.client.session
        session.save()
        session_key = session.session_key

        UserCart.objects.create(product=self.test_product,user=self.registered_user, quantity=1, session_key=session_key)
        # Логинюсь
        response = self.client.post(self.path, {
            'username': 'testuser',
            'password': 'complexpassword123'
        }, follow=True)
        test_logger.info(f"инфа о юзере {self.registered_user}")
        # Проверяем что корзина перенеслась к пользователю
        after_login_cart=UserCart.objects.filter(user=self.registered_user)
        self.assertEqual(after_login_cart.count(),1)
        self.assertEqual(after_login_cart.first().product.name,'test_product')
        


        
    
class UserProfileTest(TestCase):
    '''Тестирование контроллера UserProfileView'''
    def setUp(self):
        self.path = reverse('all_users:current_profile')
        self.test_user = StoreUser.objects.create_user(username='testuser',first_name='test_name',last_name='test_last_name',
                                                 password='complexpassword123',email='test@example.com')
    def test_base_view(self):
        '''базовое тестирование контроллера на подключениее по данному url, наличие шаблона и т.д'''
        self.client.force_login(self.test_user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store_users/profile.html')
        self.assertIn('form', response.context.keys())
        self.assertIsInstance(response.context['form'], UserProfileForm)

    def test_valid_profile_change(self):
        '''тест на успешное изменение данных в профиле'''
        # входим в учетку зареганного юзера
        login_data = {'username': 'testuser',
                      'password': 'complexpassword123'
                      }
        response = self.client.post(self.path,login_data, follow=True)
        self.assertEqual(response.status_code, 200) # проверка на вхожление в профиль
    def test_login_redirect(self):
        '''проверка что не зареагнный юзер не может зайти, введя id в url'''
        response = self.client.get(self.path)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,f'/store_users/login/?next={self.path}')  # проверка на верный редирект

    def test_successful_profile_update(self):
        '''Проверка на изменение валидных данных в профиле'''
        self.client.force_login(self.test_user)# логиним тестового юзера
        data_for_change = {'username' : 'new_test_name',
                           'first_name' : 'new_first_name',
                           'last_name' : 'new_last_name',
                           'email' : 'updated@example.com'}
        response = self.client.post(self.path, data_for_change) 
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, reverse_lazy('all_users:current_profile'))
        success_message = list(get_messages(response.wsgi_request)) # мб не сработает
        self.assertEqual(len(success_message), 1)
        test_logger.info(f"инфа мз сообщение {success_message}")
        self.assertIn("Данные в вашем профиле успешно изменены", str(success_message[0]))
        # проверка изменения данных
        updated_user = StoreUser.objects.get(pk=self.test_user.pk)
        self.assertEqual(updated_user.username, 'new_test_name')
        self.assertEqual(updated_user.email, 'updated@example.com')
        


    def test_invalid_data_update(self):
        '''тест для проверки что нельзя поменять mail на уже занятый кем то'''
        self.client.force_login(self.test_user)
        invalid_data_for_change = {'username' : '',
                                   'email': 'здарова'}
        response = self.client.post(self.path, invalid_data_for_change)
        self.assertEqual(response.status_code,200)
        error_message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(error_message), 1)
        self.assertIn("Пожалуйста введтие корректные данные", str(error_message[0]))


class UserCartTest(TestCase):
    '''Тестирование контроллера UserCartView'''
    def setUp(self):
        self.path = reverse('all_users:user_cart')
    def test_base_view(self):
        '''базовое тестирование контроллера на подключение, верность шаблона'''
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store_users/user_cart.html')