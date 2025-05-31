from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from typing import Any, Dict
from ..repositories import CartRepository, ProductRepository
from ..models import Cart, CartItem, Order, OrderDetails
import json

class CartView(LoginRequiredMixin, ListView):
    """View for displaying the user's cart."""
    model = CartItem
    template_name = 'shop/cart.html'
    context_object_name = 'cart_items'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()
        self.product_repository = ProductRepository()

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

class UpdateCartView(LoginRequiredMixin, View):
    """View for updating cart item quantities."""
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()
        self.product_repository = ProductRepository()

    def post(self, request, *args, **kwargs):
        """Handle POST request to update cart item quantity."""
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
                product_id = data.get('product_id')
                quantity = int(data.get('quantity', 0))
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': 'داده‌های نامعتبر'
                }, status=400)

            cart = self.cart_repository.get_by_user(request.user.id)
            if not cart:
                return JsonResponse({
                    'status': 'error',
                    'message': 'سبد خرید یافت نشد.'
                }, status=404)

            if not product_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'شناسه محصول الزامی است.'
                }, status=400)

            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                if self.cart_repository.remove_item(cart.id, product_id):
                    return JsonResponse({
                        'status': 'success',
                        'message': 'محصول از سبد خرید حذف شد.',
                        'cart_total': self.cart_repository.get_cart_total(cart.id),
                        'cart_count': cart.total_items
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'خطا در حذف محصول از سبد خرید.'
                    }, status=400)

            # Update item quantity
            product = self.product_repository.get_by_id(product_id)
            if not product:
                return JsonResponse({
                    'status': 'error',
                    'message': 'محصول یافت نشد.'
                }, status=404)

            if quantity > product.stock:
                return JsonResponse({
                    'status': 'error',
                    'message': 'موجودی کافی نیست.'
                }, status=400)

            if self.cart_repository.update_item_quantity(cart.id, product_id, quantity):
                return JsonResponse({
                    'status': 'success',
                    'message': 'سبد خرید با موفقیت بروزرسانی شد.',
                    'cart_total': self.cart_repository.get_cart_total(cart.id),
                    'cart_count': cart.total_items
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
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, *args, **kwargs):
        """Handle POST request to remove item from cart."""
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
                product_id = data.get('product_id')
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                return JsonResponse({
                    'status': 'error',
                    'message': 'داده‌های نامعتبر'
                }, status=400)

            cart = self.cart_repository.get_by_user(request.user.id)
            if not cart:
                return JsonResponse({
                    'status': 'error',
                    'message': 'سبد خرید یافت نشد.'
                }, status=404)

            if not product_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'شناسه محصول الزامی است.'
                }, status=400)

            if self.cart_repository.remove_item(cart.id, product_id):
                return JsonResponse({
                    'status': 'success',
                    'message': 'محصول با موفقیت از سبد خرید حذف شد.',
                    'cart_total': self.cart_repository.get_cart_total(cart.id),
                    'cart_count': cart.total_items
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

class ClearCartView(LoginRequiredMixin, View):
    """View for clearing the entire cart."""
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def post(self, request, *args, **kwargs):
        """Handle POST request to clear cart."""
        cart = self.cart_repository.get_by_user(request.user.id)
        if not cart:
            messages.error(request, 'Cart not found.')
            return redirect('shop:cart')

        if self.cart_repository.clear_cart(cart.id):
            messages.success(request, 'Cart cleared successfully.')
        else:
            messages.error(request, 'Failed to clear cart.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Cart cleared successfully.',
                'cart_total': 0,
                'cart_count': 0
            })

        return redirect('shop:cart')

class CheckoutView(LoginRequiredMixin, View):
    """View for checkout process."""
    template_name = 'shop/checkout.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_repository = CartRepository()

    def get(self, request):
        """Handle GET request for checkout page."""
        # Get or create cart for the user
        cart = self.cart_repository.get_or_create_cart(request.user.id)
        cart_items = cart.items.all()
        total = cart.total_price
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total': total,
            'is_cart_empty': not cart_items.exists()  # Add flag for empty cart
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle POST request for checkout submission."""
        cart = self.cart_repository.get_or_create_cart(request.user.id)
        
        # Check if cart is empty before processing order
        if not cart.items.exists():
            messages.error(request, 'سبد خرید شما خالی است.')
            return redirect('shop:checkout')

        # Create order
        order = Order.objects.create(
            costumer=request.user,
            address=request.POST.get('address'),
            zipcode=request.POST.get('zipcode'),
            phone=request.POST.get('phone'),
            notes=request.POST.get('notes', '')
        )

        # Create order details
        for item in cart.items.all():
            OrderDetails.objects.create(
                order=order,
                Item=item.product,
                quantity=item.quantity,
                price=item.price
            )

        # Clear and deactivate cart
        cart.clear()
        cart.is_active = False
        cart.save()
        
        messages.success(request, 'سفارش شما با موفقیت ثبت شد.')
        return redirect('shop:success') 