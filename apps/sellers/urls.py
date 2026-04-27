from django.urls import path
from .views import (
    SellerRegisterView, SellerProfileView,
    SellerListView, SellerDetailView,
    SellerDocumentView, SellerPromotionView,
    SellerDocumentUploadView
)

urlpatterns = [
    # Seller
    path('register/', SellerRegisterView.as_view(), name='seller-register'),
    path('profile/', SellerProfileView.as_view(), name='seller-profile'),
    path('documents/', SellerDocumentView.as_view(), name='seller-documents'),
    path('documents/upload/', SellerDocumentUploadView.as_view(), name='seller-document-upload'),
    path('promotions/', SellerPromotionView.as_view(), name='seller-promotions'),

    # Admin
    path('admin/list/', SellerListView.as_view(), name='seller-list'),
    path('admin/<int:pk>/', SellerDetailView.as_view(), name='seller-detail'),
]