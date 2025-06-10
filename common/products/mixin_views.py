from products.models import Product
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, SearchHeadline # для продвинутого поиска по товарам

class CommonFilterMixin():
    '''Миксин для осуществления фильтрации на странгице по цене, скидкам
    содержит проверку на фильтрацию + сам алгоритм запроса фильтрации из БД'''


    def check_filtration(self):
        '''Метод для проверки, была ли на странице применена фильтрация по товарам
        ,если да, то в GET прийдет либо on_sale либо order_by, т.к я их в input полях в шаблоне прописал'''
        if self.request.GET.get('on_sale',False) or self.request.GET.get('order_by', False):
            return True
        return False
    
    def get_filtered_products(self)->Product:
        # Получаем параметры фильтрации из запроса
        order_by = self.request.GET.get('order_by', 'default')
        on_sale = self.request.GET.get('on_sale', None)
        
        # Определяем набор категорий для фильтрации
        if hasattr(self, 'current_category') and self.current_category:
            if self.current_category.is_leaf_node():# если самая нижняя подкатегория без наслдеников
                categories = [self.current_category]
            else:
                categories = self.current_category.get_descendants(include_self=True)
        else:
            categories = []
        
        # Базовый queryset
        products = Product.objects.filter(
            Q(category__in=categories) if categories else Q(),
            is_active=True
        ).select_related('category')
        
        # Фильтры
        if on_sale:
            products = products.filter(discount__gt=0) # покажем продукты с скидкой
        
        if order_by and order_by != 'default' and order_by in ['price', '-price', 'name', '-name']:
            products = products.order_by(order_by)
            
        return products
    
class CommonSearchMixin():
    '''Миксин для проверки запроса со страницы на поиск и реализации алгоримта поиска товаров по имнеи , описанию или id'''
    
    def q_search(self,query)->Product:
        '''Алгоритм поиска товаров на сайте в поле Поиск'''
        # сначала поиск по id
        if isinstance(query, str):
            if all(map(lambda figure: figure.isdigit(),query)):# если был записан id
                products_search = Product.objects.filter(id=int(query))
                if products_search:
                    return products_search
            else:
                vector = SearchVector('name','description')
                query = SearchQuery(query)
                result = (Product.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by("-rank"))


                result= result.annotate(
                        headline=SearchHeadline(
                           "name",
                             query,
                             start_sel='<span style="background-color: yellow;">',
                            stop_sel="</span>",
                         ))
                result= result.annotate(
                        headline=SearchHeadline(
                           "description",
                             query,
                             start_sel='<span style="background-color: yellow;">',
                            stop_sel="</span>",
                         ))
                return result
                                
                # РУЧНОЙ АЛГОРИТМ ПОИСКА ПО ОПИСАНИЮ И ИМЕНИ
                keywords = [word for word in query.split() if len(word)>2] # ключевые слова из поиска, исключили предлоги
                q_objects = Q()
                for token in keywords: # добавляем слова из описания
                    q_objects |=Q(description__icontains=token)# слова для поиска в описании
                    q_objects |=Q(name__icontains=token)# слова ля поиска в имени
                return Product.objects.filter(q_objects)  # поиск по названию товара и описанию, не чувствительно к регистру
            
                return  Product.objects.filter(Q(description__search=query)|Q(name__search=query))# встроенный в django поиск по описанию и имени
    def check_search(self):
        '''Метод для проверки, если был поиск по опред товарам'''
        search_info = self.request.GET.get('q', None)
        if search_info:
            search_products = self.q_search(search_info) # q_search из utils.py где прописан алгоритм поиска
            return search_products
        return False 
    