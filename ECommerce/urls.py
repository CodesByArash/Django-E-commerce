"""Ecommerce URL Configuration

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

from django.contrib import admin
from django.urls import path,include
from shop import views

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from azbankgateways.urls import az_bank_gateways_urls
from shop.views.payment_views import go_to_gateway_view, callback_gateway_view


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('account/', include('account.urls')),
    path('api/account/', include('api.api_account.urls')),
    path('api/shop/', include('api.api_shop.urls')),

    #bank gateways
    path('bankgateways/', az_bank_gateways_urls()),
    # path('go-to-gateways/', go_to_gateway_view, name = "go-to-gateway"),
    path('callback-gateway/', callback_gateway_view, name = "call-back-gateway"),

    #drf_yasg
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)