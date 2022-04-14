from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    is_author = models.BooleanField(default=False,verbose_name="وضعیت کاربر مدیر")
    zipcode   = models.CharField(max_length=10,verbose_name='کد پستی',blank=True)
    address   = models.CharField(max_length=1000,verbose_name='آدرس',blank=True)
    city      = models.CharField(max_length=1000,verbose_name='شهر',blank=True)
    phone     = models.CharField(max_length=1000,verbose_name='شماره تلفن',blank=True)

    