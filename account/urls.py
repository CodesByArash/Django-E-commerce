from shop.models import Product
from django.contrib.auth import views
from django.urls import path
from .views import ProductDelete, orderListview, orderDetailView, ProductCreate, ProductUpdate, productlistview, Profile, signup

app_name = 'account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    # path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
urlpatterns += [
    path('',orderListview.as_view(),name="home"),
    path('detail/<int:order>/',orderDetailView,name='order'),
    path('product/create/',ProductCreate.as_view(),name="product-create"),
    path('product/',productlistview,name="products"),
    path('product/update/<int:pk>/',ProductUpdate.as_view(),name="product-update"),
    path('product/delete/<int:pk>/',ProductDelete.as_view(),name="product-delete"),
    path('signup/',signup,name="signup"),
    path('profile/<int:pk>/',Profile.as_view(),name="profile"),
    ]
