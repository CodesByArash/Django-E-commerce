from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from typing import Any, Dict
from ..repositories import ProductRepository, CategoryRepository, CartRepository
from ..models import Product, Category
from django.http import Http404
from django.core.paginator import Paginator

class IndexView(ListView):
    """View for displaying all products."""
    template_name = 'shop/index.html'
    context_object_name = 'product_obj'
    paginate_by = 8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()

    def get_queryset(self):
        """Get products with optional search filter."""
        search_query = self.request.GET.get('item_name')
        return self.product_repository.get_all(
            page=self.request.GET.get('page'),
            per_page=self.paginate_by,
            search_query=search_query
        )

    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.product_repository.get_all_categories()
        return context

class ProductDetailView(DetailView):
    """View for displaying product details."""
    template_name = 'shop/detail.html'
    context_object_name = 'product_obj'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()

    def get_object(self, queryset=None):
        """Get product by ID."""
        return self.product_repository.get_by_id(self.kwargs['id'])

    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.product_repository.get_all_categories()
        return context

class AddToCartView(LoginRequiredMixin, DetailView):
    """View for adding a product to cart."""
    model = Product
    http_method_names = ['post']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()
        self.cart_repository = CartRepository()

    def post(self, request, *args, **kwargs):
        """Handle POST request to add product to cart."""
        product = self.get_object()
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'تعداد باید بیشتر از صفر باشد.')
            return redirect('shop:detail', pk=product.id)
        
        # دریافت یا ایجاد سبد خرید
        cart = self.cart_repository.get_or_create_cart(request.user.id)
        
        # اضافه کردن محصول به سبد خرید
        cart_item = self.cart_repository.add_item(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity
        )
        
        if cart_item:
            messages.success(request, f'{product.title} به سبد خرید اضافه شد.')
        else:
            messages.error(request, 'خطا در اضافه کردن محصول به سبد خرید.')
            return redirect('shop:detail', pk=product.id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'{product.title} به سبد خرید اضافه شد.',
                'cart_count': cart.total_items
            })
        
        return redirect('shop:cart')

class CategoryView(ListView):
    """View for displaying products in a category."""
    template_name = 'shop/category.html'
    context_object_name = 'products'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()

    def get_queryset(self):
        """Get products in category."""
        return self.product_repository.get_by_category(self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        """Add category to context."""
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['slug'], status=True)
        return context 