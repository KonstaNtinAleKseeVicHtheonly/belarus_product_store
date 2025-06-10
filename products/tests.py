from django.test import TestCase
from django.urls import reverse # для тестирвоания url
#импорт моделей
from .models import Product, ProductCategory
# логгирование
import logging
from logger.project_logger import configure_logging
# установить coverage покрытие процент покрытия тестами
# прочие приблуды 
from django.core.exceptions import ObjectDoesNotExist
test_logger = logging.getLogger(__name__)

configure_logging(level='INFO')

# Create your tests here.

class MainPageTest(TestCase):
    '''Тестирование для контроллера MainPageView'''
    def test_view(self):
        path = reverse('main_page')
        response = self.client.get(path)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'products/main.html')
        

    

class ShowCatalogTest(TestCase):
    '''Тестирование для контроллера MainPageView'''

    def test_view(self):
        '''ТЕсты на базовое подключение к контроллеру по url и прочее'''
        test_logger.info('начало теста test_view_products приложения products')
        path = reverse('all_products:products_catalog')
        response = self.client.get(path)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response, 'products/catalog.html')
        test_logger.info('конец test_view_products приложения products')



class CategoryListTest(TestCase):
    '''Тестирование для контроллера CategoryListView'''

    def setUp(self):
        self.test_category = ProductCategory.objects.create(name='test_category',slug='test-category')
        ProductCategory.objects.create(name='test_category_2', slug='test-category-2')
        ProductCategory.objects.create(name='test_category_3', slug='test-category-3')
        self.all_categories = ProductCategory.objects.all()

    def test_view(self):
        '''проверка базового подключения к контроллеру, существоавания шаблона'''

        test_logger.info('начало test_view category приложения products')
        path = reverse('all_products:subcategories',kwargs={'slug' :'test-category'})
        response = self.client.get(path)

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'products/sub_categories.html')

    def test_category_creation(self):
        '''тестирование создания категорий'''
        self.assertEqual(self.test_category.name, 'test_category')
        self.assertEqual(self.test_category.slug, 'test-category')
        self.assertEqual(self.test_category.is_active, True) # проверка создания атрибутов по умолчанию
        self.assertEqual(len(self.all_categories),3)

    def test_query_objects(self):
        '''проверка отображения на страницах объектов модели ProductCategory'''

        path = reverse('all_products:subcategories',kwargs={'slug' : 'test-category'})
        # path = 'products/category/test-category/'
        response = self.client.get(path)
        test_logger.info(f'инфа из контекста {response.context.keys()}')
        self.assertEqual(response.context['all_categories'].count(), self.all_categories.count())
        self.assertIn('subcategories',response.context.keys())



    


class CurrentProductTest(TestCase):
    '''Тестирование для контроллера CurrentProductView'''

    def setUp(self):
        test_category = ProductCategory.objects.create(name='test_category',slug='test-category')
        self.test_product = Product.objects.create(name='test_product',slug='test-product', category=test_category,price=3,discount=10,weight=30, image='edas')
        Product.objects.create(name='test_product_2',category= test_category,slug='test-product-2', price=30,quantity=9,discount=10,energy_value='10г 5г 20г 150ккал',image='dasdas')

    def test_view(self):
        '''базовая проверка соединения и шаблона'''

        path = reverse('all_products:current_product',kwargs={'slug':'test-product'})
        response = self.client.get(path)
        test_logger.info(f'инфа о шаблонах {[i.name for i in response.templates]}')
        self.assertTemplateUsed(response, 'products/certain_product.html')
        self.assertEqual(response.status_code,200)

    def test_product_creation(self):
        '''проверка корректности добавления новых продуктов'''

        test_logger.info('начало теста test_product_creation приложения products')
        self.assertEqual(self.test_product.price, 3)
        self.assertEqual(self.test_product.category.name, 'test_category')
        self.assertEqual(self.test_product.slug,'test-product')
        self.assertEqual(self.test_product.is_active, True) # проверка установка значений по умолчанию
        self.assertEqual(self.test_product.discount, 10)
        self.assertEqual(self.test_product.weight, 30)

    def test_product_get_all_products(self):
        '''Проверка получения всех записей из бд модели Product'''

        test_logger.info('начало теста test_product_get_all_products приложения products')
        products = Product.objects.all()
        self.assertEqual(len(products), 2)
        test_logger.info('конец теста test_product_get_all_products приложения products')
    
   



class SalesProductTest(TestCase):
    '''Тестирование для контроллера Salesproductview'''
    
    def setUp(self):
        test_category = ProductCategory.objects.create(name='test_category', slug='test-category')
        discount_product_1 = Product.objects.create(name='product_1',category=test_category,price=30,quantity=3, discount=10, image='mda')# товары со скидкой   
        discount_product_2 = Product.objects.create(name='product_2',category=test_category,price=50,quantity=5, discount=20, image='das')
        discount_product_3 = Product.objects.create(name='product_3',category=test_category,price=50,quantity=5,  image='dadass') # товра без скидки

    def test_view(self):
        '''базовое тестирование представления'''

        test_logger.info('начало теста test_view в SalesProducts приложения products')
        path = reverse('all_products:discount')
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/sales.html')
        self.assertEqual(response.context['title'], 'Товары по акции')
        test_logger.info('конец теста test_view в SalesProduct приложения products')
        test_logger.info(f"Инфа из response {response.context['object_list']}")

    def test_logic(self):
        '''тест на отображения в шаблоне только товаров со скидкой'''

        test_logger.info('начало теста test_logic в SalesProducts приложения products')
        path = reverse('all_products:discount')
        response = self.client.get(path)
        self.assertEqual(response.context['object_list'].count(),2) # должны отобразиться только 2 продукта со скидкой, а не 3

        test_logger.info('конец теста test_logic в SalesProducts приложения products')