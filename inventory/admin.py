from django.contrib import admin
from .models import Material, Supplier, Delivery, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'brand',
        'material_type',
        'color',
        'quantity_in_stock',
        'unit'
    ]

    list_filter = [
        'material_type',
        'brand',
        'categories',
        'has_thermal_break'
    ]

    search_fields = [
        'name',
        'brand',
        'series',
        'color'
    ]

    filter_horizontal = ['categories']

    fieldsets = (
        ('Основна информация', {
            'fields': ('name', 'material_type', 'color', 'categories')
        }),
        ('Данни за профили (PVC/Алуминий)', {
            'fields': (
                'brand',
                'series',
                'profile_type',
                'chamber_count',
                'has_thermal_break',
                'bar_length'
            ),
            'classes': ('collapse',),
            'description': 'Приложимо само за профили'
        }),
        ('Складова информация', {
            'fields': ('quantity_in_stock', 'unit')
        }),
    )


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'phone', 'email']

    fieldsets = (
        ('Основна информация', {
            'fields': ('name', 'is_active')
        }),
        ('Контактна информация', {
            'fields': ('contact_person', 'phone', 'email', 'address')
        }),
        ('Допълнително', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['material', 'supplier', 'quantity', 'delivery_date', 'total_price', 'invoice_number']
    list_filter = ['delivery_date', 'supplier', 'material__material_type']
    search_fields = ['material__name', 'supplier__name', 'invoice_number']
    date_hierarchy = 'delivery_date'

    readonly_fields = ['created_at', 'total_price']

    fieldsets = (
        ('Основна информация', {
            'fields': ('material', 'supplier', 'delivery_date')
        }),
        ('Количество и цена', {
            'fields': ('quantity', 'price_per_unit', 'total_price')
        }),
        ('Документи', {
            'fields': ('invoice_number', 'notes')
        }),
        ('Системна информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def total_price(self, obj):
        return f"{obj.total_price:.2f} лв"

    total_price.short_description = 'Обща цена'

