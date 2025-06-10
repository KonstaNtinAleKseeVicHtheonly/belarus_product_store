from django.db import models
from django.utils.text import slugify 
from django.urls import reverse
from django.shortcuts import get_object_or_404
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.safestring import mark_safe

class ProductCategory(MPTTModel):
    '''Категории, подкатегории товаров.Древовидная структура'''
    name = models.CharField('Название', max_length=100, unique=True)
    slug = models.SlugField('URL', max_length=100, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True,
                            blank=True,
                            related_name='children',
                            verbose_name='parent'
                            )
    image = models.ImageField(upload_to='category_images',null=True,blank=True)
    description = models.TextField('Описание',null=True,blank=True)
    is_active = models.BooleanField('В_наличии', default=True)
# category.get_descendants(include_self=True).products.all()# получить доступ к продуктом текущей категории
    class MPTTMeta:
        order_insertion_by = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        if not self.is_active:
            return f"Категория {self.name} - недоступна"
        return f"Категория {self.name} - доступна"

    def get_absolute_url(self):
        '''Для формирования ссылки перехода по каждой категории'''
        return reverse('all_products:subcategories', kwargs={'slug': self.slug})
    

class Product(models.Model):
    '''Карточки продуктов с их ценой, описанием и прочими характеристиками'''
    category = TreeForeignKey(to=ProductCategory,
                              on_delete=models.PROTECT,
                              related_name='products',
                              verbose_name='category'
                              )
    name = models.CharField('Название', max_length=255)
    quantity = models.PositiveIntegerField(default=1)# количество товаров в магазине, инфа для админа
    slug = models.SlugField('URL', max_length=255, unique=True)
    description = models.TextField('Описание', null= True,blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    discount = models.DecimalField(
        'Скидка на товар',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    discount_price = models.PositiveIntegerField(null=True,blank=True)# заменен методом calculate_sell_price,потом удалить
    image = models.ImageField('Изображение', upload_to='products/',null=True,blank=True)
    is_active = models.BooleanField('Активен', default=True)
    delivered = models.DateField(blank=True, null=True)# когда доставлено
    energy_value = models.TextField(blank=True,null=True)# передавать через запятую бжу текстом '10г 5г 20г 150ккал'
    weight = models.PositiveIntegerField(blank=True, null=True)# вес товара

    def save(self, *args, **kwargs):
        if not self.slug: # Генерация slug если он пустой или имя товара изменилось
            original_slug = slugify(self.name)
            unique_slug = original_slug
            counter = 1
            # Проверяем уникальность slug
            while Product.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{original_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        # Корректный расчёт цены со скидкой
        self.calculate_sell_price()
        
        return super().save(*args, **kwargs)
        
    def calculate_sell_price(self):
        '''расчет цены товара с учетом скидки, если она есть'''
        if self.discount:# если есть скидка
            self.discount_price = float(self.price) * (100 - float(self.discount)) / 100
            return round(self.discount_price,2)
        else:# просто цена товара без скидки

            return round(self.price,2)
    
    def __str__(self):
        if not self.is_active:
            return f"Товар {self.name} - нет в наличии"
        return f"Товар {self.name} - есть в наличии"

    
    def products_in_tree(request, category_slug):
        '''метод позволяет получить товары из категорий и подкатегорий '''
        category = get_object_or_404(ProductCategory, slug=category_slug)
        # Используем MPTT-методы для выборки
        products = Product.objects.filter(
            category__in=category.get_descendants(include_self=True)
        )
        return products
    def get_absolute_url(self):
        '''метод определяем абсолютную ссылку на данный продукт по слагу(также нужно для правки продукта в админ панели)'''
        # return reverse('all_products:current_product', kwargs={'product_id': self.id})
        return reverse('all_products:current_product', kwargs={'slug': self.slug})
    
    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']