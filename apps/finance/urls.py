from django.urls import path
from .views import (
    FeeStructureView,
    SellerStatementListView, SellerStatementDetailView,
    SaleRecordListView,
    AdminStatementListView, AdminStatementDetailView,
    AdminSaleRecordCreateView
)

urlpatterns = [
    # General
    path('fees/', FeeStructureView.as_view(), name='fee-structure'),

    # Seller
    path('statements/', SellerStatementListView.as_view(), name='statement-list'),
    path('statements/<int:pk>/', SellerStatementDetailView.as_view(), name='statement-detail'),
    path('sales/', SaleRecordListView.as_view(), name='sale-records'),

    # Admin
    path('admin/statements/', AdminStatementListView.as_view(), name='admin-statement-list'),
    path('admin/statements/<int:pk>/', AdminStatementDetailView.as_view(), name='admin-statement-detail'),
    path('admin/sales/', AdminSaleRecordCreateView.as_view(), name='admin-sale-create'),
]