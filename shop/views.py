from django.core import paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import OrderDetails, Product, Order, Category, Cart, CartItem
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

# Create your views here.



def index(request):
    product_obj     = Product.objects.all()

    item_name       = request.GET.get('item_name')
    
    if item_name   != '' and item_name is not None:
        product_obj = Product.objects.filter(title__icontains=item_name)

    paginator       = Paginator(product_obj,8)
    page            = request.GET.get('page')
    product_obj     = paginator.get_page(page)

    return render(request,'shop/index.html',{'product_obj':product_obj,'category':Category.objects.all()})
    

def detail(request,id):
    product_obj = Product.objects.get(id=id)
    return render(request,'shop/detail.html',{
        'product_obj': product_obj,
        'category': Category.objects.all()
    })

@login_required
def checkout(request):
    """صفحه نهایی خرید و پرداخت"""
    try:
        cart = Cart.objects.get(user=request.user, is_active=True)
    except Cart.DoesNotExist:
        # اگر سبد خرید فعال نداشت، به صفحه اصلی برو
        return redirect('shop:index')
        
    cart_items = cart.items.all()
    
    if request.method == 'POST':
        # ایجاد سفارش جدید
        order = Order.objects.create(
            costumer=request.user,
            total=str(cart.total_price),
            status='p'  # در حال پردازش
        )
        
        # انتقال آیتم‌های سبد خرید به جزئیات سفارش
        for item in cart_items:
            OrderDetails.objects.create(
                order=order,
                Item=item.product,
                quantity=str(item.quantity),
                price=str(item.price)
            )
        
        # پاک کردن سبد خرید
        cart.items.all().delete()
        cart.is_active = False
        cart.save()
        
        return redirect('shop:success')
    
    # محاسبه قیمت کل
    total = cart.total_price
    
    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def add_to_cart(request, product_id):
    """اضافه کردن محصول به سبد خرید"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # دریافت یا ایجاد سبد خرید
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        
        # اضافه کردن محصول به سبد
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price': product.price
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'محصول به سبد خرید اضافه شد',
            'cart_items_count': cart.total_items
        })
    
    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'})

@login_required
def update_cart(request, product_id):
    """بروزرسانی تعداد محصول در سبد خرید"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        quantity = int(request.POST.get('quantity', 0))
        
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'سبد خرید بروزرسانی شد',
            'cart_total': cart.total_price,
            'cart_items_count': cart.total_items
        })
    
    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'})

@login_required
def remove_from_cart(request, product_id):
    """حذف محصول از سبد خرید"""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'محصول از سبد خرید حذف شد',
            'cart_total': cart.total_price,
            'cart_items_count': cart.total_items
        })
    
    return JsonResponse({'status': 'error', 'message': 'متد نامعتبر'})

def success(request):

    return render(request,"shop/success.html")


def category(request,slug):
    context={
        "category":get_object_or_404(Category,slug=slug , status=True)
    }
    product = Product.objects.filter(category)

    return render(request, "shop/category.html")