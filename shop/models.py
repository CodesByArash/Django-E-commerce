from typing import ItemsView
from django.db import models
from account.models import User
from django.db.models.deletion import CASCADE
from django.db.models.fields import SlugField
from django.utils import tree
from django.utils import timezone
from extensions.utils import jalali_converter
# Create your models here.



class Category(models.Model):
    title =models.CharField(max_length=200 , verbose_name="دسته بندی",)
    Slug = models.CharField(max_length=200 , verbose_name="آدرس",)
    status = models.BooleanField(default=True , verbose_name="نمایش داده شود؟",)
    position = models.IntegerField(verbose_name='موفعیت')
    class Meta:
        verbose_name="دسته بندی"
        verbose_name_plural='دسته بندی ها'
        
    
        

class Product(models.Model):
    
    title          = models.CharField(max_length=200)
    price          = models.FloatField()
    discount_price = models.FloatField()
    category       = models.ManyToManyField(Category,)
    description    = models.TextField()
    image          = models.ImageField(upload_to="images")

    def __str__(self):
        return super().__str__()

    class Meta:
        verbose_name="محصول"
        verbose_name_plural='محصولات'

class Order(models.Model):
    STATUS_CHOICES =(
        ('s','ارسال شده'),
        ('p','در حال پردازش'),
        ('r','رسیده به دست مشتری'),
    )
    costumer = models.ForeignKey(User, on_delete=CASCADE,verbose_name='نام مشتری')
    items    = models.CharField(max_length=1000,verbose_name='محصولات')
    date     = models.DateTimeField(default=timezone.now(), verbose_name='تاریخ ثبت',)
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