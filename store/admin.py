from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at', 'updated_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_discounted', 'is_latest', 'created_at']
    list_filter = ['category', 'is_discounted', 'is_latest', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_discounted', 'is_latest']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'price')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Flags', {
            'fields': ('is_discounted', 'is_latest')
        }),
    )
