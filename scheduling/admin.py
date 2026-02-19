from django.contrib import admin
from .models import Installation

@admin.register(Installation)
class InstallationAdmin(admin.ModelAdmin):
    list_display = ['order', 'scheduled_date']
