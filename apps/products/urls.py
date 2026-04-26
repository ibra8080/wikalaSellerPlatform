from django.urls import path
from .views import (
    CategoryListView,
    ProductListCreateView, ProductDetailView,
    AdminProductListView, AdminProductDetailView,
    ProductVariantView, ProductPromotionView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),

    # Seller
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/variants/', ProductVariantView.as_view(), name='product-variants'),
    path('promotions/', ProductPromotionView.as_view(), name='product-promotions'),

    # Admin
    path('admin/list/', AdminProductListView.as_view(), name='admin-product-list'),
    path('admin/<int:pk>/', AdminProductDetailView.as_view(), name='admin-product-detail'),
]