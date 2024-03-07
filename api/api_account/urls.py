from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import *


urlpatterns = [
    path('register/', Register.as_view()),
    path('auth-token/', obtain_auth_token),
    path('revoke-token/', RevokeToken.as_view()),
    path('verify-email/<slug:token>/', verify_email),
    path('request-verification/',request_email_verification, name="request-verification"),
    path('forget-password/', ForgetPassword.as_view(), name='forget-password'),
    path('reset-password/<uidb64>/<token>/', ResetPassword.as_view(), name='reset-password'),
    path('change-password/', ChangePassword.as_view(), name='change-password')
]
