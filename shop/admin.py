from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from .models import Product, Order,Category,OrderDetails
# Register your models here.


admin.site.site_header = "فروشگاه"
admin.site.site_title  = "پنل مدیریت فروشگاه"
admin.site.index_title = "مدیریت سفارشات"





class ProductAdmin(admin.ModelAdmin):

    list_display = ('title','price','discount_price','description')
    def category_to_str(sef,obj):
        return ", ".join([category.title for category in obj.category.all()])

    category_to_str.short_description="دسته بندی"


class OrderAdmin(admin.ModelAdmin):

    list_display = ('costumer','items','jpublish','status','total')
    search_fields= ('category',)
    list_filter  = ('date','status')
    search_fields = ('title','')
    ordering = ['-status','-date']


class CategoryAdmin(admin.ModelAdmin):

    list_display = ('title','Slug','status','position')
    search_fields= ('category',)
    list_filter  = ('title','status')
    search_fields = ('title','')
    

admin.site.register(OrderDetails)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order,OrderAdmin)
