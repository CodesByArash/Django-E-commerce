from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, EmailOTP
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

UserAdmin.fieldsets[2][1]['fields']=(
    'is_active',
    'is_staff',
    'is_superuser',
    'is_author',
    'groups',
    'user_permissions')

UserAdmin.list_display +=('is_author',)


admin.site.register(User,UserAdmin)
