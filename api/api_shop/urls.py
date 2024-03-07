from django.urls import path, include
from .views import *


urlpatterns = [
    path('latest_products/', LatestProductsList.as_view()),
    path('search/', search),
    path('slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view()),
    path('categories/', create_category),
    path('slug:category_slug>/', CategoryDetail.as_view()),    
]

 