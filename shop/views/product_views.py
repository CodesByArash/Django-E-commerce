from django.views.generic import ListView, DetailView, TemplateView
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
        context['categories'] = self.product_repository.get_all_categories()
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
        context['categories'] = self.product_repository.get_all_categories()
        return context

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
        context['current_category'] = get_object_or_404(Category, slug=self.kwargs['slug'], status=True)
        context['categories'] = self.product_repository.get_all_categories()
        return context

class SearchView(ListView):
    """View for displaying search results."""
    template_name = 'shop/search.html'
    context_object_name = 'products'
    paginate_by = 8

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = ProductRepository()

    def get_queryset(self):
        """Get products matching search query."""
        search_query = self.request.GET.get('q')
        if not search_query:
            return Product.objects.none()
        return self.product_repository.search_by_title(
            search_query,
            page=self.request.GET.get('page'),
            per_page=self.paginate_by
        )

    def get_context_data(self, **kwargs):
        """Add search query and categories to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['categories'] = self.product_repository.get_all_categories()
        return context

class CategoriesView(TemplateView):
    """View for displaying all categories in a dedicated page."""
    template_name = 'shop/categories_page.html'

    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['categories_tree'] = Category.objects.filter(
            parent__isnull=True, 
            status=True
        ).prefetch_related(
            'children__children__children__children__children'
        )
        return context 