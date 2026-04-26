from django.urls import path
from .views import (
    SellerContractListView, SellerContractDetailView,
    AdminContractListCreateView, AdminContractDetailView,
    ShippingFeeOptionView, ShippingFeeOptionDetailView
)

urlpatterns = [
    # Seller
    path('', SellerContractListView.as_view(), name='contract-list'),
    path('<int:pk>/', SellerContractDetailView.as_view(), name='contract-detail'),
    path('shipping/', ShippingFeeOptionView.as_view(), name='shipping-fee'),
    path('shipping/<int:pk>/', ShippingFeeOptionDetailView.as_view(), name='shipping-fee-detail'),

    # Admin
    path('admin/', AdminContractListCreateView.as_view(), name='admin-contract-list'),
    path('admin/<int:pk>/', AdminContractDetailView.as_view(), name='admin-contract-detail'),
]