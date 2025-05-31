"""DrugStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, re_path

from django.contrib import admin
from django.urls import path,include
from shop import views
from .views.product_views import ProductListView, ProductDetailView, AddToCartView, CategoryView
from .views.cart_views import UpdateCartView, RemoveFromCartView, ClearCartView, CheckoutView
from django.views.generic import TemplateView, RedirectView

app_name="shop"
urlpatterns = [
    # Product URLs
    path('', ProductListView.as_view(), name='index'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('cart/add/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    
    # Cart URLs - Redirect cart to checkout
    path('cart/', RedirectView.as_view(pattern_name='shop:checkout', permanent=True), name='cart'),
    path('cart/update/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', TemplateView.as_view(template_name='shop/success.html'), name='success'),
]

