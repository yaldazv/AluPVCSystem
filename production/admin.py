from django.contrib import admin
from .models import Category, Order, CustomProduct, ReadyProduct


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'system_offset']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'status', 'created_at', 'customer_phone']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'delivery_address']
    date_hierarchy = 'created_at'


@admin.register(CustomProduct)
class CustomProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_type',
        'category',
        'width',
        'height',
        'sash_count',
        'opening_type',
        'order'
    ]

    list_filter = [
        'product_type',
        'category',
        'opening_type'
    ]

    search_fields = [
        'order__id',
        'order__customer_name'
    ]

    filter_horizontal = ['materials']

    fieldsets = (
        ('Основна информация', {
            'fields': ('order', 'category', 'product_type')
        }),
        ('Размери и конфигурация', {
            'fields': (
                'width',
                'height',
                'sash_count',
                'opening_type'
            )
        }),
        ('Материали', {
            'fields': ('materials',)
        }),
    )


@admin.register(ReadyProduct)
class ReadyProductAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'quantity',
        'unit_price',
        'order'
    ]

    search_fields = [
        'name',
        'order__customer_name'
    ]
