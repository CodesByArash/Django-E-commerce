from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from typing import Any, Dict
from ..repositories import CartRepository, ProductRepository
from ..models import Cart, CartItem, Order, OrderItem
from shop.models import Product
from .payment_views import go_to_gateway_view
import json

class CartView(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'shop/cart.html'
    context_object_name = 'cart_items'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def get_queryset(self):
        cart = self.cart_repository.get_by_user(self.request.user.id)
        if cart:
            return cart.items.all()
        return CartItem.objects.none()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = self.cart_repository.get_by_user(self.request.user.id)
        if cart:
            context['cart'] = cart
            context['total'] = self.cart_repository.get_cart_total(cart.id)
        return context

class AddToCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            with transaction.atomic():
                cart = self.cart_repository.get_or_create_cart(request.user)
                quantity = int(request.POST.get('quantity', 1))
                
                if quantity <= 0:
                    messages.error(request, 'تعداد باید بیشتر از صفر باشد.')
                    return redirect('shop:detail', id=product_id)
                
                # Lock the product to check quantity
                product = Product.objects.select_for_update().get(id=product_id)
                
                if quantity > product.quantity:
                    messages.error(request, 'موجودی کافی نیست.')
                    return redirect('shop:detail', id=product_id)
                
                cart_item, created = self.cart_repository.add_item(cart, product, quantity)
                
                messages.success(request, 'محصول به سبد خرید اضافه شد')
                return redirect('shop:checkout')
                
        except Exception as e:
            messages.error(request, f'خطای سیستمی: {str(e)}')
            return redirect('shop:detail', id=product_id)

class UpdateCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                if self.cart_repository.remove_item(cart, product_id):
                    messages.success(request, 'محصول از سبد خرید حذف شد.')
                else:
                    messages.error(request, 'خطا در حذف محصول از سبد خرید.')
                return redirect('shop:checkout')
            
            product = Product.objects.select_for_update().get(id=product_id)
            
            if quantity > product.quantity:
                messages.error(request, 'موجودی کافی نیست.')
                return redirect('shop:checkout')
            
            cart_item = self.cart_repository.update_item_quantity(cart, product_id, quantity)
            if cart_item:
                messages.success(request, 'سبد خرید بروزرسانی شد.')
            else:
                messages.error(request, 'خطا در بروزرسانی سبد خرید.')
            
            return redirect('shop:checkout')
            
        except Exception as e:
            messages.error(request, f'خطای سیستمی: {str(e)}')
            return redirect('shop:checkout')

class RemoveFromCartView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            if self.cart_repository.remove_item(cart, product_id):
                messages.success(request, 'محصول از سبد خرید حذف شد')
            else:
                messages.error(request, 'خطا در حذف محصول از سبد خرید.')
            return redirect('shop:checkout')
            
        except Exception as e:
            messages.error(request, f'خطای سیستمی: {str(e)}')
            return redirect('shop:checkout')

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/checkout.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def get_context_data(self, **kwargs):
        """Get cart items and total for checkout."""
        context = super().get_context_data(**kwargs)
        cart = self.cart_repository.get_active_cart(self.request.user)
        
        if cart and cart.items.exists():
            context['cart_items'] = cart.items.all()
            context['total'] = cart.total_price
            context['is_empty'] = False
        else:
            context['cart_items'] = []
            context['total'] = 0
            context['is_empty'] = True
            
        return context

    def post(self, request, *args, **kwargs):
        cart = self.cart_repository.get_active_cart(request.user)
        if not cart or not cart.items.exists():
            messages.error(request, 'سبد خرید شما خالی است.')
            return redirect('shop:checkout')
        
        shipping_address = request.POST.get('address', '').strip()
        if not shipping_address:
            messages.error(request, 'لطفا آدرس ارسال را وارد کنید.')
            return redirect('shop:checkout')
        # try:
        #     order = self.cart_repository.create_order(cart, shipping_address)
        #     messages.success(request, 'سفارش شما با موفقیت ثبت شد.')
        #     return redirect('shop:success')
        # except ValueError as e:
        #     messages.error(request, f'خطا در ثبت سفارش: {str(e)}')
        #     return redirect('shop:checkout')
        # except Exception as e:
        #     messages.error(request, 'خطای سیستمی در ثبت سفارش. لطفاً دوباره تلاش کنید.')
        #     return redirect('shop:checkout')
        request.session['shipping_address'] = shipping_address
        return go_to_gateway_view(request)

        


class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest order for the current user
        try:
            order = Order.objects.filter(user=self.request.user).latest('created_at')
            context['order'] = order
            context['order_items'] = order.items.all()
            context['status_display'] = dict(Order.STATUS_CHOICES)[order.status]
        except Order.DoesNotExist:
            context['order'] = None
            context['order_items'] = []
            context['status_display'] = None
        return context 


class FailureView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/failure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the latest payment for the current user
        try:
            from shop.models import Payment
            payment = Payment.objects.filter(user=self.request.user).latest('created_at')
            context['payment'] = payment
        except Payment.DoesNotExist:
            context['payment'] = None
        return context 