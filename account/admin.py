from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

UserAdmin.fieldsets[2][1]['fields']=(
    'is_active',
    'is_staff',
    'is_superuser',
    'is_author',
    'groups',
    'user_permissions')

UserAdmin.list_display +=('is_author',)

admin.site.register(User,UserAdmin)