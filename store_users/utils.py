# импорт моделей
from carts.models import UserCart
# утитлиты
from django.contrib import auth, messages
from django.http import UnreadablePostError

def check_unlogin_carts(request,form):
    '''Доп метод для контроллера UserLoginView, для сохранения корзины, которую
    добавил юзер до авторизации, через сессионные ключи'''
    session_key = request.session.session_key
    current_user = form.get_user()
    if current_user:
        auth.login(request, current_user) # логиним юзера если она есть в системе
        if session_key:
            previous_carts = UserCart.objects.filter(user=current_user) # удалим старые корзины если были
            if not previous_carts.exists():
                request.session.cycle_key()
            # if previous_carts.exists(): # возможно удалить
            #     previous_carts.delete() 
            # else:
            #     request.session.cycle_key()
        UserCart.objects.filter(session_key=session_key).update(user=current_user) # добавлем корзины котоыре блыи до авторизации
    else:
        return messages(request,"ПОжалуйста проверьте данные, такого пользователя нет в системе")
    