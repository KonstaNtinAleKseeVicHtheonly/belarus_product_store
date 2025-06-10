from django.urls import path
from .views import about_view, StaffView
from django.views.decorators.cache import cache_page

app_name ='additional'

urlpatterns = [
    path('about/', cache_page(60*5)(about_view), name='about'),
    path('staff/',StaffView.as_view(),name='staff')
    ]


