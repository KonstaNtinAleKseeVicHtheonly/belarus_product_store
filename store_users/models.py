from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class StoreUser(AbstractUser):
    '''Модель пользователей магазина с личными данными, фото, также применяется для форм автор и аутентификации
    Мы расширяем базовую таблицу из auth'''
    image = models.ImageField(upload_to='user_images',null=True, blank=True, verbose_name='Аватарка')
    email = models.EmailField(verbose_name='адрес электронной почты', unique=True)
    phone_number = models.CharField(max_length=18, blank=True, null= True)
    code_word = models.CharField(max_length=15, verbose_name='кодовое слово', null=True,blank=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):

            if self.is_superuser:
                return f"Пользователь {self.username} с правами админа"
            elif self.is_staff:
                 return f"Пользователь {self.username} с правами работника"
            return f"Пользователь {self.username}"
    
    def get_full_name(self):
         return super().get_full_name()