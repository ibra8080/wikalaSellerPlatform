from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Certification, ProductPromotion


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'parent')
    search_fields = ('name_en', 'name_ar')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name_en', 'seller', 'status', 'price', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('product_code', 'name_en', 'seller__business_name')
    readonly_fields = ('product_code', 'created_at', 'updated_at')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('sku', 'product', 'color', 'size', 'quantity_submitted')
    search_fields = ('sku',)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'type', 'uploaded_at')


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    list_display = ('product', 'promo_type', 'value', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active', 'promo_type')