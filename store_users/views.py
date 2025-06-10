#базовые утилилиты
from django.contrib import auth, messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
# импорт базовых контроллеров
from django.contrib.auth.views import LoginView # вьюха для авторизации
from django.views.generic.edit import UpdateView, CreateView, FormView # вьюхи для регистрации и профиля юзера
from django.views.generic import TemplateView
#импорт миксинов
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin # для корректной рабоыт профиля юзера 
from django.contrib.auth.decorators import login_required# что бы незашедший юзер не мог выйти
# импорт моделей
from django.db.models import Prefetch # для рьратного поиска от Foreign key моделей
from .models import StoreUser
from carts.models import UserCart # корзины пользователей
from orders.models import UserOrders, OrderItem
# импорт форм
from .forms import UserLoginForm, UserRegistrationForm, UserProfileForm, VerifyCodeWordForm, NewPasswordForm
#логер
import logging
# доп утилитиы 
from django.core.cache import cache # для кэшироввания
from .utils import check_unlogin_carts # метод для переноса корзин юзера до авторизации через сессионные ключи


user_logger = logging.getLogger(__name__)


# Create your views here.

class UserRegistrationView(SuccessMessageMixin,CreateView):
    '''контроллер для регистрации пользовталея в магазе'''
    # model = StoreUser
    form_class = UserRegistrationForm
    template_name = 'store_users/registration.html'
  
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = 'Регистрация пользователя'

        return context
    
    def get_success_url(self):
        '''При успешной авторизации - перенаправляю на главную страницу'''
        messages.success(self.request, f"ПОздравляю с успешной регистрацией, {self.request.user.username}.Удачных покупок!")# сообщение при входе в аккаунт

        return reverse_lazy('all_users:current_profile')
    
    def form_valid(self, form):
        '''Расшири метод, что бы полсе регисрации у юзера сохранялась корзина после регистрации'''

        session_key = self.request.session.session_key# сохраняем сессионный ключ юзера до регистрации
        current_user = form.instance # инфа юзера из формы 

        if current_user:
            form.save() 
            auth.login(self.request,current_user)# что бы юзер логинился после регистрации сразу
            if session_key:
                UserCart.objects.filter(session_key=session_key).update(user=current_user)
            else:# обновляем сессию если ключа не было
                self.request.session.cycle_key()
            return HttpResponseRedirect(self.get_success_url())# отправим на страницу авторизации
            

    

class UserLoginView(LoginView):
    '''Контроллер для авторизации юзера'''
    template_name = 'store_users/login.html'
    form_class = UserLoginForm # форма, связанная с моделью
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = 'Авторизация пользователя'
        return context
    
    def get_success_url(self):
        '''При успешной авторизации - перенаправляю на главную страницу'''
        messages.success(self.request, f"Добро пожаловать в свой профиль, {self.request.user.username}")# сообщение при входе в аккаунт

        return reverse_lazy('all_users:current_profile')
    
    def form_valid(self, form):
        '''Расширил метод чтобы корзины добавленные до авторизации сохранялись после нее'''
        check_unlogin_carts(self.request, form)
        return HttpResponseRedirect(self.get_success_url())
        # если через утилиту не сработае, вод сам код
        # session_key = self.request.session.session_key # сохрняем ключ сессии до авторизации что бы не затерся
        # current_user = form.get_user() # объект юзера по форме после его аутентификации
        # if current_user:
        #     auth.login(self.request, current_user)# логиним юзера если она есть в системе
        #     if session_key:
        #         forgotten_carts = UserCart.objects.filter(user=current_user)# старые корзины юзера еще до авторизации
        #         forgotten_carts.delete()
        #     else:
        #         self.request.session.cycle_key()# обновим сессию на всякий случай
        #     UserCart.objects.filter(session_key=session_key).update(user=current_user) # обновлем корзину юзера полсе авторизации


class UserProfileView(LoginRequiredMixin,UpdateView):
    '''контроллер для отображения, rud операций профиля юзера'''
    model = StoreUser # не удалять иначе ошибку будет ImproperlyConfigured 
    form_class = UserProfileForm
    template_name = 'store_users/profile.html'
    success_url = reverse_lazy('all_users:current_profile') #  в случае изменения профился, юзера на его же профиль и перенаправит

    def form_valid(self, form):
        messages.success(self.request,f"Данные в вашем профиле успешно изменены")
        return super().form_valid(form)
    
    def form_invalid(self, form): 

        messages.error(self.request, f"Пожалуйста введтие корректные данные")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs)-> dict:
            context =  super().get_context_data(**kwargs)
            context['title'] = 'Ваш профиль'
            #кэшируем индивидуальные заказы пользователя
            user_orders = cache.get(f"{self.request.user.id}_user_orders")
            if not user_orders:
                user_orders = UserOrders.objects.filter(user=self.request.user).prefetch_related(Prefetch('order_items',
                                                                                                            queryset=OrderItem.objects.select_related("product"),
                                                                                                            )).order_by('-id') # заказы юзера обратный поиск от foreign_key в OrderItem
                cache.set(f"{self.request.user.id}_user_orders",user_orders,3600) # если такой пары в кэше не было, создаем ее
            context['orders'] = user_orders
            return context
    
    def get_object(self, queryset = None):
        '''Метод нужен, что бы нельзя было перейти на другого пользоватлея, прпоисав другой id в url'''
        queryset = self.get_queryset()# список всех юзеров
        current_user = queryset.get(pk=self.request.user.id)
        return current_user

class UserCartView(TemplateView):
    '''Контроллер для отображения корзины товаров текущего пользователя''' 
    template_name = 'store_users/user_cart.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина пользователя'
        context['certain_title'] = f"Корзина {self.request.user.username}(а)"
        return context
    
# class UserChangePassword(FormView):
#     '''контроллер для смены пароля, при вводе валидных логина, почти и телефона'''
#     template_name = 'store_users/change_password.html'

#     def get_form_class(self):
#         # Определяем, какую форму отдать в зависимости от состояния сессии
#         if 'verified' in self.request.session:
#             return NewPasswordForm
#         return VerifyCodeWordForm
#     def get_context_data(self, **kwargs):
#         context= super().get_context_data(**kwargs)
#         if 'verified' not in self.request.session:
#             context['step'] = 1
#             context['title'] = 'Верификация пользователя'
#             messages.success(self.request, 'Пожалуйста верифицируйте данные')
#             return context
#         else:
#             context['step'] = 2
#             messages.success(self.request, 'Введите новый пароль')
  
#             return context
#     def form_valid(self, form):
#         if isinstance(form, VerifyCodeWordForm):
#             # Первый шаг — проверка кодового слова
#             self.request.session['verified'] = True
#             self.request.session['username'] = form.cleaned_data['username']
#             self.request.session['email'] = form.cleaned_data['email']
#             messages.success(self.request, "Кодовое слово подтверждено. Введите новый пароль.")
#             return HttpResponseRedirect(reverse('all_users:change_password'))  # редирект к этому же view, но уже на второй шаг
#         elif isinstance(form, NewPasswordForm):
#             username = self.request.session.get('username')
#             email = self.request.session.get('email')
#             if not username:
#                 messages.error(self.request, "Сессия устарела. Повторите процедуру.")
#                 return HttpResponseRedirect(reverse('all_users:change_password'))
#             try:
#                 current_user = StoreUser.objects.get(username=username, email=email)
#             except Exception as err:
#                 messages.error(self.request, f"Юзер не найден {err}")
#                 return HttpResponseRedirect(reverse('all_users:change_password'))

#             current_user.set_password(form.cleaned_data['password1'])
#             current_user.save()
#             # Очистка сессии
#             self.request.session.pop('verified', None)
#             self.request.session.pop('username', None)
#             self.request.session.pop('email', None)
#             messages.success(self.request, 'Пароль успешно изменен, пожалуйста авторизуйтесь')
#             return HttpResponseRedirect(reverse('all_users:current_login'))
#         return HttpResponseRedirect(reverse('all_users:current_login'))
        
#     def form_invalid(self, form):
#             messages.error(self.request,'Введите валидные данные')
#             return super().form_invalid(form)
            
    
    
class UserVerifyView(FormView):
    '''контроллер для верификации пользователя, что бы допустить к измнению пароля'''
    template_name = 'store_users/change_password.html'
    form_class = VerifyCodeWordForm

    def form_valid(self, form):
            # Первый шаг — проверка кодового слова
            self.request.session['verified'] = True
            self.request.session['username'] = form.cleaned_data['username']
            self.request.session['email'] = form.cleaned_data['email']
            messages.success(self.request, "Верификация прошла успешна, введите новый пароль" )
            user_logger.info(f"Инфа из формы{form.cleaned_data}") 
            return HttpResponseRedirect(reverse('all_users:change_password'))


    def form_invalid(self, form):
            messages.error(self.request,'Пожалуйста введите валидный данные')
            return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        if 'verified' not in self.request.session:
            context['step'] = 1
            context['title'] = 'Верификация пользователя'
            context['form_action'] = reverse('all_users:verify_user')  # определяет action  в тэге форм
            messages.success(self.request, 'Пожалуйста верифицируйте данные')
            return context
        else: # если юзер уже верифицирован, сразу редирект на смену паролч
            context['title'] = 'Смена пароля'
            context['step'] = 2
            context['form_action'] = reverse('all_users:verify_user') # определяет action  в тэге форм
        return context
    
class UserChangePassword(FormView):
    '''контроллер для изменения пароля поле верификации'''
    template_name = 'store_users/change_password.html'
    form_class = NewPasswordForm


    def dispatch(self, request, *args, **kwargs):
        '''Действия до обработки get, post запросов.Здесь    проверка, что бы юзер не проскочил верификацию'''
        if 'verified' not in request.session:
            messages.error(request, "Сначала пройдите верификацию.")
            return HttpResponseRedirect(reverse('all_users:verify_user'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        
        username = self.request.session['username']
        email = self.request.session['email']
        user_logger.info(f"инфа из form_valid {self.request.session.items()}")
        user_logger.info(f"инфа из формы  {form.cleaned_data.items()}")

        if not username or not email:
            messages.error(self.request, "Сессия устарела. Пройдите верификацию снова.")
            return HttpResponseRedirect(reverse('all_users:verify_user'))
        try:
            current_user =StoreUser.objects.get(username = username, email=email)
        except StoreUser.DoesNotExist as err:
            messages.error(self.request, 'Пользователь с указанными данными не найден')
            return HttpResponseRedirect(reverse('all_users:verify_user'))   
        user_logger.info(f"инфа о смене парл {form.cleaned_data.items()}")
        current_user.set_password(form.cleaned_data['password1'])
        current_user.save()
        user_logger.info(f"Инфа из формы{form.cleaned_data}")
        #очистка сессии 
        for key in ['verified', 'username', 'email']:
            self.request.session.pop(key, None)
        messages.success(self.request, 'Данные успешно изменены, пожалуйста авторизируйтесь с новым паролем')
        
        return HttpResponseRedirect(reverse('all_users:current_login'))
    
    def form_invalid(self, form):
        messages.error(self.request,  "Ошибка при смене пароля. Проверьте поля.")
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Смена пароля'
        context['step'] = 2
        context['form_action'] = reverse('all_users:change_password') # определяет action  в тэге форм
        return context
        
    

  


@login_required(login_url='main_page') # при попытке выйти не автор. юзера, перенаправляю на main_page
def logout(request):
    '''Функция для осуществления выхода юзера из профиля'''
    auth.logout(request)  # выход пользователя из системы
    # возврат юзера на главную страницу после выхода
    messages.success(request, f"{request.user.username} Вы вышли из своего аккаунта")# сообщение при выходе из аккаунта
    return HttpResponseRedirect(reverse("main_page"))