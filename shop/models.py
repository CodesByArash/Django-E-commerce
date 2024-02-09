from typing import ItemsView
from django.db import models
from account.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields import SlugField
from django.utils import tree
from django.utils import timezone
from extensions.utils import jalali_converter
from PIL import Image
from io import BytesIO
from django.core.files import File

# Create your models here.



class Category(models.Model):
    title    = models.CharField(max_length=200 , verbose_name="دسته بندی",)
    Slug     = models.CharField(max_length=200 , verbose_name="آدرس",)
    status   = models.BooleanField(default=True , verbose_name="نمایش داده شود؟",)
    position = models.IntegerField(verbose_name='موفعیت')

    class Meta:
        ordering = ['title',]
        verbose_name="دسته بندی"
        verbose_name_plural='دسته بندی ها'
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f'/{self.slug}/'
    
        

class Product(models.Model): 
    title          = models.CharField(max_length=200)
    slug           = models.SlugField()
    discount_price = models.FloatField()
    category       = models.ManyToManyField(Category, related_name='products')
    description    = models.TextField(blank=True, null=True)
    price          = models.DecimalField(max_digits = 6, decimal_places=2)
    image          = models.ImageField(upload_to="images")
    thumbnail      = models.ImageField(upload_to='uploads/', blank=True, null=True)
    date_added     = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return super().__str__()

    class Meta:
        ordering = ['-date_added',]
        verbose_name="محصول"
        verbose_name_plural='محصولات'
    
    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'
    
    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000'+self.thumbnail.url
        else:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()
            return 'http://1277.0.01:8000'+ self.thumbnail.url
    
    def make_thumbnail(self, image, size=(300, 200)):
        img       = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io  = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name= image.name)

        return thumbnail
    

class Order(models.Model):
    STATUS_CHOICES =(
        ('s','ارسال شده'),
        ('p','در حال پردازش'),
        ('r','رسیده به دست مشتری'),
    )
    costumer = models.ForeignKey(User, on_delete=CASCADE,verbose_name='نام مشتری')
    items    = models.CharField(max_length=1000,verbose_name='محصولات')
    date     = models.DateTimeField(default=timezone.now, verbose_name='تاریخ ثبت',)
    status   = models.CharField(max_length=1, choices=STATUS_CHOICES,verbose_name='وضعیت سفارش',default=STATUS_CHOICES[1][1])
    total    = models.CharField(max_length=200,verbose_name="قیمت کل")
    class Meta:
        verbose_name="سفارش"
        verbose_name_plural='سفارشات'

    def jpublish(self):
        return  jalali_converter(self.date)
    
    jpublish.short_description = "زمان انتشار"



class OrderDetails(models.Model):
    order    = models.ForeignKey(Order,on_delete=CASCADE)
    Item     = models.ForeignKey(Product,on_delete=CASCADE)
    quantity = models.CharField(max_length=100)
    price    = models.CharField(max_length=300,blank=True)
    class Meta:
        verbose_name="جزییات سفارش"
        verbose_name_plural="جزییات سفارشات"