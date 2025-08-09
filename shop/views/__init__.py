from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .product_views import (
    IndexView, ProductDetailView, CategoryView, SearchView, CategoriesView,
)
from .cart_views import (
    CheckoutView, AddToCartView, UpdateCartView, RemoveFromCartView, SuccessView, FailureView,
)


__all__ = [
    # Product views
    'IndexView', 'ProductDetailView', 'CategoryView', 'SearchView', 'CategoriesView',
    # Cart views
    'CheckoutView', 'AddToCartView', 'UpdateCartView', 'RemoveFromCartView', 'SuccessView', 'FailureView',
] 

