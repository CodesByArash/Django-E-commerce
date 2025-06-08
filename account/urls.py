from django.urls import path
from account.views import (
    RegisterView, ProfileView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    OrderListView, OrderDetailView, OrderUpdateView
)
from account.views.auth_views import CustomLoginView as LoginView, CustomLogoutView as LogoutView

app_name = 'account'

urlpatterns = [
    # User authentication views
    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    
    # Product management URLs
    path('products/', ProductListView.as_view(), name='products'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    # Order management URLs
    path('orders/', OrderListView.as_view(), name='orders'),
    path('orders/<int:order>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
] 