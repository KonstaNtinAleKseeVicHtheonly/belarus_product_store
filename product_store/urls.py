"""
URL configuration for product_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # главный сайт с настройками(если product_store.settings не будут работаь)
from django.conf.urls.static import static
from product_store.settings import DEBUG
from products.views import MainPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainPageView.as_view(),name='main_page'),
    path('products/', include('products.urls', namespace='all_products')),
    path('additional/', include('additional_info.urls', namespace='additional')),
    path('store_users/', include('store_users.urls', namespace='all_users')),
    path('carts/', include('carts.urls', namespace='all_carts')),
    path('orders/', include('orders.urls', namespace='all_orders'))
    ] 


if DEBUG: # будет работать только в режиме разработке, не в продакшене
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))] 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # путь до папки с медиа
