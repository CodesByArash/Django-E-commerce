from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""
    class Meta:
        model = Product
        fields = ['title', 'price', 'discount_price', 'category', 'description', 'image', 'quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.CheckboxSelectMultiple(),
            'quantity': forms.NumberInput(attrs={'min': 0}),
        }
        labels = {
            'title': 'عنوان محصول',
            'price': 'قیمت',
            'discount_price': 'قیمت با تخفیف',
            'category': 'دسته‌بندی',
            'description': 'توضیحات',
            'image': 'تصویر محصول',
            'quantity': 'تعداد موجودی',
        }
        help_texts = {
            'discount_price': 'قیمت با تخفیف را وارد کنید (اختیاری)',
            'category': 'دسته‌بندی‌های محصول را انتخاب کنید',
            'description': 'توضیحات کامل محصول را وارد کنید',
            'image': 'تصویر محصول را انتخاب کنید',
            'quantity': 'تعداد موجودی محصول در انبار را وارد کنید',
        } 