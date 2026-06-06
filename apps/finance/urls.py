from django.urls import path
from .views import (
    FeeStructureView,
    SellerStatementListView, SellerStatementDetailView,
    SaleRecordListView,
    AdminStatementListView, AdminStatementDetailView,
    AdminSaleRecordCreateView, StatementCalculateView,
    WebServiceListView,
    AdminWebServiceListCreateView, AdminWebServiceDetailView,
    AdminDiscountCodeListCreateView, AdminDiscountCodeDetailView,
    ApplyDiscountCodeView, SellerActiveCodesView,
    AdminSellerDiscountListCreateView, AdminSellerDiscountDetailView,
    SellerChargesListView,
    AdminChargesListCreateView, AdminChargeDetailView,
    AdminCreateRegistrationChargeView,
    SellerActivateServiceView,
)

urlpatterns = [
    # General
    path('fees/', FeeStructureView.as_view(), name='fee-structure'),

    # Seller
    path('statements/', SellerStatementListView.as_view(), name='statement-list'),
    path('statements/<int:pk>/', SellerStatementDetailView.as_view(), name='statement-detail'),
    path('sales/', SaleRecordListView.as_view(), name='sale-records'),
    path('services/', WebServiceListView.as_view(), name='service-list'),
    path('charges/', SellerChargesListView.as_view(), name='seller-charges'),
    path('codes/apply/', ApplyDiscountCodeView.as_view(), name='apply-code'),
    path('codes/', SellerActiveCodesView.as_view(), name='seller-codes'),

    # Admin
    path('admin/statements/', AdminStatementListView.as_view(), name='admin-statement-list'),
    path('admin/statements/calculate/', StatementCalculateView.as_view(), name='statement-calculate'),
    path('admin/statements/<int:pk>/', AdminStatementDetailView.as_view(), name='admin-statement-detail'),
    path('admin/sales/', AdminSaleRecordCreateView.as_view(), name='admin-sale-create'),
    path('admin/services/', AdminWebServiceListCreateView.as_view(), name='admin-service-list'),
    path('admin/services/<int:pk>/', AdminWebServiceDetailView.as_view(), name='admin-service-detail'),
    path('admin/codes/', AdminDiscountCodeListCreateView.as_view(), name='admin-code-list'),
    path('admin/codes/<int:pk>/', AdminDiscountCodeDetailView.as_view(), name='admin-code-detail'),
    path('admin/discounts/', AdminSellerDiscountListCreateView.as_view(), name='admin-discount-list'),
    path('admin/discounts/<int:pk>/', AdminSellerDiscountDetailView.as_view(), name='admin-discount-detail'),
    path('admin/charges/', AdminChargesListCreateView.as_view(), name='admin-charge-list'),
    path('admin/charges/<int:pk>/', AdminChargeDetailView.as_view(), name='admin-charge-detail'),
    path('admin/charges/registration/<int:seller_id>/', AdminCreateRegistrationChargeView.as_view(), name='admin-registration-charge'),
]