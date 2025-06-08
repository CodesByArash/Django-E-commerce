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
from django.urls import path
from django.views.generic import RedirectView
from .views import (
    # Product views
    IndexView, ProductDetailView, CategoryView,
    # Cart views
    CheckoutView, AddToCartView, UpdateCartView, RemoveFromCartView, SuccessView,
    # Order views
    OrderListView, OrderDetailView,
)

app_name = "shop"

urlpatterns = [
    # Product URLs
    path('', IndexView.as_view(), name='index'),
    path('product/<int:id>/', ProductDetailView.as_view(), name='detail'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
    
    # Cart URLs
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:product_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('success/', SuccessView.as_view(), name='success'),
    
    # Order URLs
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:order>/', OrderDetailView.as_view(), name='order-detail'),
]

