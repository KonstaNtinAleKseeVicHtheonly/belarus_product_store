from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from products.models import ProductCategory
from store_users.models import StoreUser

# Create your views here.


def about_view(request):
    '''Контроллер для описания магазина, предоставления инфы о нем'''
    context = dict()
    context['title'] = 'О нас'
    context['all_categories'] = ProductCategory.objects.filter(
            level=0, 
            is_active=True
        )

    return render(request, 'additional_info/about.html',context=context)




class StaffView(ListView):
    '''Предоставляет инфу о персонале магазина'''
    model = StoreUser
    template_name = 'additional_info/staff.html'
    pagginated_by = 3
    context_object_name = 'employees'

    def get_queryset(self):
        '''Переопределил мето что бы пагинация работала по работникам'''

        return StoreUser.objects.filter(is_staff=True)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['director'] = StoreUser.objects.get(username='Konstantin')
        return context