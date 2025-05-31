from django.views.generic import ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from typing import Any, Dict
from ..repositories import CartRepository, ProductRepository
from ..models import Cart, CartItem, Order, OrderDetails
from shop.models import Product
import json

class CartView(LoginRequiredMixin, ListView):
    """View for displaying the user's cart."""
    model = CartItem
    template_name = 'shop/cart.html'
    context_object_name = 'cart_items'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def get_queryset(self):
        """Get the cart items for the current user."""
        cart = self.cart_repository.get_by_user(self.request.user.id)
        if cart:
            return cart.items.all()
        return CartItem.objects.none()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        cart = self.cart_repository.get_by_user(self.request.user.id)
        if cart:
            context['cart'] = cart
            context['total'] = self.cart_repository.get_cart_total(cart.id)
        return context

class AddToCartView(LoginRequiredMixin, View):
    """View for adding items to cart."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        """Add product to cart."""
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            product = get_object_or_404(Product, id=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity <= 0:
                return JsonResponse({
                    'status': 'error',
                    'message': 'تعداد باید بیشتر از صفر باشد.'
                }, status=400)
            
            if quantity > product.stock:
                return JsonResponse({
                    'status': 'error',
                    'message': 'موجودی کافی نیست.'
                }, status=400)
            
            cart_item, created = self.cart_repository.add_item(cart, product, quantity)
            
            return JsonResponse({
                'status': 'success',
                'message': 'محصول به سبد خرید اضافه شد',
                'cart_items_count': cart.total_items,
                'cart_total': cart.total_price
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'خطای سیستمی: {str(e)}'
            }, status=500)

class UpdateCartView(LoginRequiredMixin, View):
    """View for updating cart items."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        """Update cart item quantity."""
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            quantity = int(request.POST.get('quantity', 0))
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                if self.cart_repository.remove_item(cart, product_id):
                    return JsonResponse({
                        'status': 'success',
                        'message': 'محصول از سبد خرید حذف شد.',
                        'cart_total': cart.total_price,
                        'cart_items_count': cart.total_items
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'خطا در حذف محصول از سبد خرید.'
                    }, status=400)
            
            product = get_object_or_404(Product, id=product_id)
            if quantity > product.stock:
                return JsonResponse({
                    'status': 'error',
                    'message': 'موجودی کافی نیست.'
                }, status=400)
            
            cart_item = self.cart_repository.update_item_quantity(cart, product_id, quantity)
            if cart_item:
                return JsonResponse({
                    'status': 'success',
                    'message': 'سبد خرید بروزرسانی شد',
                    'cart_total': cart.total_price,
                    'cart_items_count': cart.total_items
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'خطا در بروزرسانی سبد خرید.'
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'خطای سیستمی: {str(e)}'
            }, status=500)

class RemoveFromCartView(LoginRequiredMixin, View):
    """View for removing items from cart."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, product_id):
        """Remove product from cart."""
        try:
            cart = self.cart_repository.get_or_create_cart(request.user)
            if self.cart_repository.remove_item(cart, product_id):
                return JsonResponse({
                    'status': 'success',
                    'message': 'محصول از سبد خرید حذف شد',
                    'cart_total': cart.total_price,
                    'cart_items_count': cart.total_items
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'خطا در حذف محصول از سبد خرید.'
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'خطای سیستمی: {str(e)}'
            }, status=500)

class CheckoutView(LoginRequiredMixin, TemplateView):
    """View for checkout process."""
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
        """Handle order creation."""
        cart = self.cart_repository.get_active_cart(request.user)
        if not cart:
            return redirect('shop:index')
            
        order = self.cart_repository.create_order(cart)
        return redirect('shop:success')

class SuccessView(TemplateView):
    """View for successful order completion."""
    template_name = 'shop/success.html' 