from django.contrib import admin
from .models import Installation

@admin.register(Installation)
class InstallationAdmin(admin.ModelAdmin):
    list_display = ['installation_date', 'address', 'status', 'get_orders_count']
    list_filter = ['status', 'installation_date']
    search_fields = ['address', 'notes']
    date_hierarchy = 'installation_date'
    filter_horizontal = ['orders']

    def get_orders_count(self, obj):
        """Показва броя поръчки за този монтаж"""
        return obj.orders.count()
    get_orders_count.short_description = 'Брой поръчки'
