from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'brand',
        'material_type',
        'color',
        'quantity',
        'unit',
        'price_per_unit'
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
            'fields': ('quantity', 'unit', 'price_per_unit')
        }),
    )
