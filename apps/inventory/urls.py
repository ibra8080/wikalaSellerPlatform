from django.urls import path
from .views import (
    SellerInventoryView, ShipmentUpdateListView,
    AdminShipmentUpdateView, AdminInventoryDetailView
)

urlpatterns = [
    # Seller
    path('', SellerInventoryView.as_view(), name='seller-inventory'),
    path('shipments/', ShipmentUpdateListView.as_view(), name='shipment-list'),

    # Admin
    path('admin/shipment/update/', AdminShipmentUpdateView.as_view(), name='admin-shipment-update'),
    path('admin/<int:pk>/', AdminInventoryDetailView.as_view(), name='admin-inventory-detail'),
]