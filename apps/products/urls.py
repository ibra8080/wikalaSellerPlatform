from django.urls import path
from .views import (
    CategoryListView,
    ProductListCreateView, ProductDetailView,
    AdminProductListView, AdminProductDetailView,
    ProductVariantView, ProductPromotionView,
    ProductImageUploadView,
    ProductVariantDetailView, ProductImageDeleteView,
    AdminProductDeleteView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),

    # Seller
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/variants/', ProductVariantView.as_view(), name='product-variants'),
    path('<int:pk>/variants/<int:variant_pk>/', ProductVariantDetailView.as_view(), name='product-variant-detail'),
    path('<int:pk>/images/upload/', ProductImageUploadView.as_view(), name='product-image-upload'),
    path('<int:pk>/images/<int:image_pk>/', ProductImageDeleteView.as_view(), name='product-image-delete'),
    path('promotions/', ProductPromotionView.as_view(), name='product-promotions'),

    # Admin
    path('admin/list/', AdminProductListView.as_view(), name='admin-product-list'),
    path('admin/<int:pk>/', AdminProductDetailView.as_view(), name='admin-product-detail'),
    path('admin/<int:pk>/delete/', AdminProductDeleteView.as_view(), name='admin-product-delete'),
]
