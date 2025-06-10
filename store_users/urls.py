from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView, logout, UserCartView, UserVerifyView, UserChangePassword
from django.contrib.auth.decorators import login_required

app_name = 'all_users'

urlpatterns = [

    path('register/', UserRegistrationView.as_view(),name='current_registration'),
    path('login/', UserLoginView.as_view(), name='current_login'),
    path('profile/', login_required(UserProfileView.as_view()),name='current_profile'),
    path('logout/', logout,name='logout'),
    path('user_cart/',UserCartView.as_view(), name='user_cart'),
    path('change_password/' , UserChangePassword.as_view(), name='change_password'),
    path('verify_data/', UserVerifyView.as_view(), name='verify_user')                  

]