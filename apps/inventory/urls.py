from django.urls import path
from .views import (
    SellerInventoryView, ShipmentUpdateListView,
    AdminShipmentUpdateView, AdminInventoryDetailView,
    ShipmentRequestListCreateView, ShipmentRequestDetailView,
    AdminShipmentRequestListView, AdminShipmentRequestDetailView,
)

urlpatterns = [
    # Seller — Inventory
    path('', SellerInventoryView.as_view(), name='seller-inventory'),
    path('shipments/', ShipmentUpdateListView.as_view(), name='shipment-list'),

    # Seller — Shipment Requests
    path('shipment-requests/', ShipmentRequestListCreateView.as_view(), name='shipment-requests'),
    path('shipment-requests/<int:pk>/', ShipmentRequestDetailView.as_view(), name='shipment-request-detail'),

    # Admin — Inventory
    path('admin/shipment/update/', AdminShipmentUpdateView.as_view(), name='admin-shipment-update'),
    path('admin/<int:pk>/', AdminInventoryDetailView.as_view(), name='admin-inventory-detail'),

    # Admin — Shipment Requests
    path('admin/shipment-requests/', AdminShipmentRequestListView.as_view(), name='admin-shipment-requests'),
    path('admin/shipment-requests/<int:pk>/', AdminShipmentRequestDetailView.as_view(), name='admin-shipment-request-detail'),
]