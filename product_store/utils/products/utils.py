from products.models import Product, ProductCategory
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)


def q_search(query):
    '''Алгоритм поиска товаров на сайте в поле Поиск'''
    # сначала поиск по id
    if isinstance(query, str) and len(query) < 2: # валидация поиска товаров
        products_search = Product.objects.filter(id=int(query))
        if products_search:
            return products_search
    else:

        products_search = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query),
        is_active = True).select_related('category')
        return products_search