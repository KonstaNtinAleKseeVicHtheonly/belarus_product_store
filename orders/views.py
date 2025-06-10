from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
# импорт моделей
from django.db.models import Prefetch # для обратного поиска от Foreign key моделей
from .models import UserOrders, OrderItem
# импорт форм
from .forms import OrderForm
#контроллеры в виде классов
from django.views.generic.edit import CreateView
#миксины
from django.contrib.auth.mixins import LoginRequiredMixin
# доп утилиты
import logging
from logger.project_logger import configure_logging
from django.forms import ValidationError
from .utils import save_orders_and_changes # содержит алгоримт добваления товара и сохранения изменений на складе товаров


# Create your views here.

logger = logging.getLogger(__name__)
configure_logging(level='INFO')

class OrderCreateView(LoginRequiredMixin,CreateView):
    '''контроллер для создания заказа юзера'''

    model = UserOrders
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    success_url = reverse_lazy('all_users:current_profile')

    def get_initial(self):
        '''метод что бы в формах заполнения заказа сохрнались записанне до этого значения'''
        initial =  super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['second_name'] = self.request.user.last_name
        initial['email'] = self.request.user.email
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            initial :dict = {'first_name' : self.request.user.first_name,
                            'last_name' : self.request.user.last_name,
                            'email' : self.request.user.email,
                            'phone_number' : self.request.user.phone_number} # сохраняю исходные данные в форсе
            current_form = OrderForm(initial=initial) # что бы поля сохранялись при неверном вводе и т.д
            context['form'] = current_form
        context['order'] = True # что бы кнопка оформления заказа не выскаивала каждый раз при измении заказа
        messages.success(self.request, "Пожалуйста введите данные для оформления заказа")
        context['title'] = 'Оформление заказа'
        return context

    def form_valid(self, form):

        logger.info(f"Вот инфа из запроса {self.request}")
        logger.info(f"Инфа о форме{form.cleaned_data}")
        form.instance.user = self.request.user # сохраняем юзера для вытаскивания инфы

        #ручной алгоритм сохранения заказов юзера (UserOrders + OrderItem)
        try:
            save_orders_and_changes(self.request, form)
            super().form_valid(form)
            return HttpResponseRedirect(reverse('all_users:current_profile'))
        except ValidationError as error:
            messages.warning(self.request, f"Извините,что то пошло не так{error}")
            return HttpResponseRedirect(reverse('all_users:current_profile'))
     
    def form_invalid(self, form):
        super().form_invalid(form)

        messages.error(self.request, "Пожалуйста введите валидные данные для оформления заказа.")

        return super().form_invalid(form)

    
    
def user_orders_view(request):
    '''Простенький контроллер для отображения инфы о заказах пользователя'''

    if request.method == 'GET':
        context = {}
        context['orders'] = UserOrders.objects.filter(user=request.user).prefetch_related(Prefetch('order_items',
                                                                                                            queryset=OrderItem.objects.select_related("product"),
                                                                                                            )).order_by('-id') # заказы юзера обратный поиск от foreign_key в OrderItem
        context['title'] = 'Заказы пользователя'
        
        return render(request, 'includes/user_orders.html', context=context)

