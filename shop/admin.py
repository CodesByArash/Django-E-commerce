from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import Product, Order, Category, OrderItem, Cart, CartItem
# Register your models here.


admin.site.site_header = "فروشگاه"
admin.site.site_title  = "پنل مدیریت فروشگاه"
admin.site.index_title = "مدیریت سفارشات"





class ProductAdmin(admin.ModelAdmin):

    list_display = ('title','price','discount_price','description')
    def category_to_str(sef,obj):
        return ", ".join([category.title for category in obj.category.all()])

    category_to_str.short_description="دسته بندی"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'total_price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'total_items', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__username', 'tracking_code')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'قیمت کل'

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'تعداد کل آیتم‌ها'


class CategoryAdmin(admin.ModelAdmin):

    list_display = ('title', 'slug', 'status', 'position')
    search_fields = ('title', 'slug')
    list_filter = ('status',)
    prepopulated_fields = {'slug': ('title',)}
    

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('price', 'total_price')

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_price', 'total_items', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'قیمت کل'

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'تعداد کل آیتم‌ها'

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'price', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'cart__user__email')
    readonly_fields = ('created_at', 'updated_at')

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'قیمت کل'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'quantity', 'price', 'total_price')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'order__user__email')
    readonly_fields = ('created_at',)

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'قیمت کل'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
