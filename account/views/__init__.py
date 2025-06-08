from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .auth_views import (
    RegisterView,
    CustomLoginView as LoginView,
    CustomLogoutView as LogoutView,
    ProfileView
)
from .product_views import (
    ProductListView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView
)
from .order_views import (
    OrderListView,
    OrderDetailView,
    OrderUpdateView,
)

__all__ = [
    # Auth views
    'RegisterView',
    'LoginView',
    'LogoutView',
    'ProfileView',
    # Product views
    'ProductListView',
    'ProductCreateView',
    'ProductUpdateView',
    'ProductDeleteView',
    # Order views
    'OrderListView',
    'OrderDetailView',
    'OrderUpdateView',
] 