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
from django.core.validators import MinValueValidator
from django.utils.text import slugify



class Category(models.Model):
    title    = models.CharField(max_length=200 , verbose_name="دسته بندی",)
    slug     = models.SlugField(max_length=200 , verbose_name="آدرس", unique=True)
    status   = models.BooleanField(default=True , verbose_name="نمایش داده شود؟",)
    position = models.IntegerField(verbose_name='موفعیت')
    parent   = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='دسته والد')

    class Meta:
        ordering = ['title',]
        verbose_name="دسته بندی"
        verbose_name_plural='دسته بندی ها'
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f'/{self.slug}/'
    
    def get_all_children(self):
        """دریافت تمام زیرمجموعه‌ها به صورت بازگشتی"""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def get_all_parents(self):
        """دریافت تمام والدین به صورت بازگشتی"""
        parents = []
        if self.parent:
            parents.append(self.parent)
            parents.extend(self.parent.get_all_parents())
        return parents
    
    def is_root(self):
        """بررسی اینکه آیا دسته‌بندی ریشه است"""
        return self.parent is None
    
    def get_level(self):
        """دریافت سطح دسته‌بندی (0 برای ریشه)"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
        

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
    quantity       = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_added',]
        verbose_name="محصول"
        verbose_name_plural='محصولات'
    
    def get_absolute_url(self):
        first_category = self.category.first()
        if first_category:
            return f'/{first_category.slug}/{self.slug}/'
        return f'/{self.slug}/'
    
    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000'+self.thumbnail.url
        else:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()
            return 'http://1277.0.01:8000'+ self.thumbnail.url
    
    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io  = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name= image.name)

        return thumbnail
    

class Cart(models.Model):
    user = models.ForeignKey(
        'account.User',
        on_delete=models.CASCADE,
        verbose_name='کاربر',
        related_name='carts'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_cart_per_user'
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_active:
            Cart.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'سبد خرید {self.user.email} - {self.created_at.strftime("%Y-%m-%d")}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='محصول'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='تعداد'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='قیمت واحد'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ اضافه شدن'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )

    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.title} - {self.quantity} عدد'

    @property
    def total_price(self):
        return self.price * self.quantity

    def increase_quantity(self, amount=1):
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='کاربر',
        related_name='orders'
    )

    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null = True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت سفارش'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='قیمت کل'
    )
    shipping_address = models.TextField(
        verbose_name='آدرس ارسال'
    )
    tracking_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='کد رهگیری پستی'
    )
    tracking_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='کد پیگیری'
    )

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    def __str__(self):
        return f'سفارش {self.user.email} - {self.created_at.strftime("%Y-%m-%d")}'

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        import random
        import string
        from datetime import datetime
        
        now = datetime.now()
        date_part = now.strftime('%y%m%d') 
        
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        tracking_number = f'ORD-{date_part}-{random_part}'
        
        while Order.objects.filter(tracking_number=tracking_number).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            tracking_number = f'ORD-{date_part}-{random_part}'
        
        return tracking_number

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='محصول'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='تعداد'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='قیمت واحد'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
        unique_together = ('order', 'product')

    def __str__(self):
        return f'{self.product.title} - {self.quantity} عدد'

    @property
    def total_price(self):
        return self.price * self.quantity
    

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('completed', 'پرداخت شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
        ('refunded', 'بازگشت وجه'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('online', 'پرداخت آنلاین'),
        ('cash', 'پرداخت نقدی'),
        ('bank_transfer', 'انتقال بانکی'),
        ('wallet', 'کیف پول'),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='کاربر',
        related_name='payments'
    )
    payment_number = models.CharField(
        max_length=100,
        verbose_name='شماره پرداخت'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='روش پرداخت'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='مبلغ پرداختی',
        null=True,
        blank=True,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت پرداخت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'پرداخت {self.payment_number} - {self.user.email}'