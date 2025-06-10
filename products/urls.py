from django.urls import path
from .views import CategoryListView, CurrentProductView,ShowCatalog,Salesproductsview, MainPageView
from django.views.decorators.cache import cache_page # для кэширования наиболее посещаемых страниц

app_name ='all_products'

urlpatterns = [
    # path('', cache_page(60*5)(MainPageView.as_view()), name='main_page'),
    path('catalog/', cache_page(60*5)(ShowCatalog.as_view()), name='products_catalog'),
    path('category/<slug:slug>/',  cache_page(30)(CategoryListView.as_view()), name='subcategories'),
    path('products/<slug:slug>/',  cache_page(30)(CurrentProductView.as_view()), name='current_product'),
    path('sales/',Salesproductsview.as_view(), name='discount'),
    path('search/', CategoryListView.as_view(), name='search')# путь для поисковой системы
    ]


