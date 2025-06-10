from carts.models import UserCart

def get_user_carts(request):
    '''утилита, что бы брать по request все корзины текущего юзера в views.py'''
    if request.user.is_authenticated:# что бы только зарегестрированный юзер мог смотреть свою корзину
        return UserCart.objects.filter(user=request.user).select_related('product') # все корзины данного юзера
    if not request.session.session_key: # если юзер не авторизован, присваиваем ему ключ сессии, что бы работала корзина для него
        request.session.create()  # генерация ключа сессии
    return UserCart.objects.filter(session_key = request.session.session_key).select_related('product') # select_related, что бы не было двойного запроса на товары из корзины
 

