from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from typing import Any, Dict
from ..repositories import CartRepository, ProductRepository
from ..models import Cart, CartItem, Order, OrderItem
from shop.models import Product
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
            cart = self.cart_repository.get_or_create_cart(request.user)
            product = get_object_or_404(Product, id=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity <= 0:
                messages.error(request, 'تعداد باید بیشتر از صفر باشد.')
                return redirect('shop:detail', id=product_id)
            
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
        """Update cart item quantity."""
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                if self.cart_repository.remove_item(cart, product_id):
                    messages.success(request, 'محصول از سبد خرید حذف شد.')
                else:
                    messages.error(request, 'خطا در حذف محصول از سبد خرید.')
                return redirect('shop:checkout')
            
            product = get_object_or_404(Product, id=product_id)
            if quantity > product.stock:
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
        if not cart:
            return redirect('shop:index')
            
        context['cart_items'] = cart.items.all()
        context['total'] = cart.total_price
        return context

    def post(self, request, *args, **kwargs):
        cart = self.cart_repository.get_active_cart(request.user)
        if not cart:
            return redirect('shop:index')
            
        order = self.cart_repository.create_order(cart)
        return redirect('shop:success')

class SuccessView(TemplateView):
    """View for successful order completion."""
    template_name = 'shop/success.html' 