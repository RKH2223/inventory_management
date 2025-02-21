# frx   om django.contrib import admin
from django.contrib import admin
from .models import Reel, DailyUsage

@admin.register(Reel)
class ReelAdmin(admin.ModelAdmin):
    list_display = ('reel_code', 'reel_type', 'size_inch', 'weight_kg', 'current_stock')
    search_fields = ('reel_code', 'reel_type')

@admin.register(DailyUsage)
class DailyUsageAdmin(admin.ModelAdmin):
    list_display = ('reel', 'used_weight', 'usage_date', 'operator')
    list_filter = ('usage_date', 'reel__reel_type')
# 
# Register your models here.
