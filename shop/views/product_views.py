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

class ProductListView(ListView):
    """View for displaying a list of products."""
    model = Product
    template_name = 'shop/index.html'
    context_object_name = 'product_obj'
    paginate_by = 8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()

    def get_queryset(self):
        """Get the list of products based on filters."""
        category_id = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_id:
            category = self.category_repository.get_by_id(int(category_id))
            if category:
                return Product.objects.filter(category=category)
        elif search_query:
            return Product.objects.filter(title__icontains=search_query)
        
        return Product.objects.all()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['categories'] = self.category_repository.get_all()
        context['category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(DetailView):
    """View for displaying product details."""
    model = Product
    template_name = 'shop/detail.html'
    context_object_name = 'product_obj'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()

    def get_object(self, queryset=None):
        """Get the product object."""
        product = self.product_repository.get_by_id(self.kwargs.get('pk'))
        if product is None:
            raise Http404("محصول مورد نظر یافت نشد")
        return product

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['categories'] = self.category_repository.get_all()
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
    model = Product
    template_name = 'shop/category.html'
    context_object_name = 'product_obj'
    paginate_by = 8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()
        self.category_repository = CategoryRepository()

    def get_queryset(self):
        """Get products in the specified category."""
        category_slug = self.kwargs.get('slug')
        category = get_object_or_404(Category, slug=category_slug)
        return self.product_repository.filter_by_category(category)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('slug')
        context['category_obj'] = get_object_or_404(Category, slug=category_slug)
        context['categories'] = self.category_repository.get_all()
        return context 