from django.contrib import admin
from .models import Product, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Класс продуктов в админке"""

    list_display = ('name', 'slug', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'rating')
    search_fields = ('author', 'text')

    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    approve_reviews.short_description = "Одобрить выбранные отзывы"
