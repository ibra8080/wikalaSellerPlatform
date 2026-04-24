from django.contrib import admin
from .models import SellerProfile, SellerTier, SellerDocument, Promotion, SellerPromotion


@admin.register(SellerTier)
class SellerTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'seller_id', 'status', 'seller_tier', 'created_at')
    list_filter = ('status', 'seller_tier')
    search_fields = ('business_name', 'seller_id', 'user__email')
    readonly_fields = ('seller_id', 'created_at', 'updated_at')


@admin.register(SellerDocument)
class SellerDocumentAdmin(admin.ModelAdmin):
    list_display = ('seller', 'doc_type', 'verified', 'uploaded_at')
    list_filter = ('doc_type', 'verified')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'is_active', 'created_at')
    list_filter = ('discount_type', 'is_active')


@admin.register(SellerPromotion)
class SellerPromotionAdmin(admin.ModelAdmin):
    list_display = ('seller', 'promotion', 'is_active', 'expires_at')
    list_filter = ('is_active',)