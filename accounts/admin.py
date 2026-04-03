from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        ('Допълнителна информация', {
            'fields': ('role', 'phone_number', 'company_name')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Допълнителна информация', {
            'fields': ('role', 'phone_number', 'company_name')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)
