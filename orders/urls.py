from django.urls import path
from .views import OrderCreateView, user_orders_view

app_name = 'all_orders'

urlpatterns = [
    path('create_order/', OrderCreateView.as_view(), name='create_order'),
    path('user_orders/', user_orders_view,name='user_orders'),
]