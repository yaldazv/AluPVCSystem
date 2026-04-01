from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('phone_number',)
    fieldsets = UserAdmin.fieldsets + (
        ('Допълнителна информация', {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Допълнителна информация', {'fields': ('phone_number',)}),
    )
