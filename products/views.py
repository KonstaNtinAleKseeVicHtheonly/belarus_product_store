from django.shortcuts import render
from django.shortcuts import get_object_or_404
#импорт представлений
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from mptt.templatetags.mptt_tags import cache_tree_children
# импорт моделей
from .models import ProductCategory, Product
#логгирование
import logging
from logger.project_logger import configure_logging
# random для генерации случайной цитаты
import random
from pathlib import Path# что бы найи путь до файла с цитатами
# кастомные миксины
from common.products.mixin_views import CommonFilterMixin, CommonSearchMixin

product_logger = logging.getLogger(__name__)
configure_logging(level='INFO')


# Create your views here.

class MainPageView(TemplateView):
    '''покажет заглавную страницу сайта'''
    template_name = 'products/main.html'
    model = ProductCategory

    def generate_quotation(self):
        '''метод берущий из файла рандомную цитату с файлика, при развертывании у вас на компе вставьте свой путь в path'''
        current_dir = Path(__file__).parent  # Директория скрипта
        file_path = current_dir / 'quotations.txt'# нахождения файла в скрипте

        with open(file_path,'r',encoding='utf-8') as refactor_quotations:
                without_space = [strow for strow in refactor_quotations if strow.strip()]
                random_quote = random.choice(without_space)
                return random_quote
        

    def get_context_data(self, **kwargs):

        context =  super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        context['all_categories'] = ProductCategory.objects.filter(level=0)
        context['main_info'] = 'Магазин для всей семьи' 
        context['quote'] = self.generate_quotation()# рандомная цитата с сайта
        
        return context



class ShowCatalog(ListView):
    '''ПОказывает каталог с корневыми категориями,подкатегориями с возможностью перехода'''

    model = ProductCategory
    template_name = 'products/catalog.html'
    context_object_name = 'subcategories'
    paginate_by = 3
    ordering = ['name']

    
    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug:
            current_category = get_object_or_404(
                self.object, 
                slug=slug,
                is_active=True
            )
            return current_category.get_children().filter(is_active=True)# пагинация переключается по подкатегориям
        return ProductCategory.objects.filter(level=0, is_active=True) # если категорий нет, корневые категории
    def get_context_data(self,**kwargs):
    
        context = super().get_context_data(**kwargs)
        root_categories = ProductCategory.objects.filter(level=0, is_active=True)# корневые категории   
        context['all_categories'] = root_categories # что бы каталог работал только, потом удалить
        context['title'] = 'Каталог товаров'
        slug = self.kwargs.get('slug')
        if slug:
            context['current_category'] = get_object_or_404(
                self.object, 
                slug=slug,
                is_active=True
            )
    
        return context

class CategoryListView(CommonFilterMixin,CommonSearchMixin, ListView):
    '''Отображает вложенные категории товаров с карточками товаров в них'''

    template_name = 'products/sub_categories.html'
    context_object_name = 'subcategories' # что бы циклом по продуктам пройти
    model = ProductCategory
    paginate_by=3

    def get_queryset(self):
        slug = self.kwargs.get('slug')
    
        if slug:
            self.current_category = get_object_or_404(
                ProductCategory, 
                slug=slug, 
                is_active=True
            )
            
            if self.current_category.is_leaf_node():
                # Для конечной категории возвращаем отфильтрованные товары, пагинация по товарам
                return self.get_filtered_products()
            else:
                # Для категории с подкатегориями возвращаем подкатегории, пагинация по категориям
                return cache_tree_children(
                    self.current_category.get_children().filter(is_active=True)
                )
        # Для корневых категорий
        return cache_tree_children(
            ProductCategory.objects.filter(level=0, is_active=True)
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        
        # Всегда добавляем корневые категории
        root_categories = ProductCategory.objects.filter(level=0, is_active=True)
        context['all_categories'] = root_categories
        if slug:
             # Добавляем информацию о текущей категории
            context.update({
                'current_category': self.current_category,
                'breadcrumbs': self.current_category.get_ancestors(include_self=True),
                'title': self.current_category.name
            })
            if self.check_filtration(): # если были запрос на фильтрацию товаров
                context['products'] = self.get_filtered_products()
            else:# иначе возвращаем товары по категории и ниже
                context['products'] = Product.objects.filter(
                        category__in=self.current_category.get_descendants(include_self=True),
                        is_active=True
                    ).select_related('category')
        else:
            if self.check_search():# если был поиск по товарам, т.к там не по слагам поиск
                context['products'] = self.check_search() # метод, проверяющий q запрос из поиска в БД


        return context



class CurrentProductView(DetailView):
    '''Отображает определенный продукт с его ценой, описанием и прочими характеристиками'''
    template_name = 'products/certain_product.html'
    slug_url_kwarg = 'slug' # для обращения в бд к опред продукту по его slug
    model = Product


    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        current_product = Product.objects.get(slug=slug)# слаг текущего продукта
        context['current_product'] = current_product
        context['category_id'] = self.kwargs.get('category_id')
        context['title'] = self.object.name # имя текущего продукта в заголовке
        context['all_categories'] = ProductCategory.objects.filter(level=0, is_active=True) # хардкод для категорий каталога
        return context
    

class Salesproductsview(CommonFilterMixin,ListView):
    '''контроллер для отображения товара по скидкам'''
    template_name = 'products/sales.html'
    model = Product
    context_object_name = 'discount_products'
    paginate_by = 6


    def get_queryset(self):
        if self.check_filtration(): # если были запрос на фильтрацию товаров
            return self.get_filtered_products()
        else:# иначе возвращаем товары по категории и ниже
            return Product.objects.filter(discount_price__gt=0, is_active=True).order_by('discount')


    
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['title'] = 'Товары по акции'
        context['all_categories'] =  ProductCategory.objects.filter(level=0, is_active=True)
    
        return context
    

