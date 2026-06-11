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
    StatementLineItemListCreateView, StatementLineItemDetailView,
    StatementGenerateView, StatementSendView, StatementMarkPaidView,
    StatementAcceptView, StatementDisputeView,
    AdminStatementDisputeResolveView,
)

urlpatterns = [
    # General
    path('fees/', FeeStructureView.as_view(), name='fee-structure'),

    # Seller
    path('statements/', SellerStatementListView.as_view(), name='statement-list'),
    path('statements/<int:pk>/', SellerStatementDetailView.as_view(), name='statement-detail'),
    path('statements/<int:pk>/accept/', StatementAcceptView.as_view(), name='statement-accept'),
    path('statements/<int:pk>/dispute/', StatementDisputeView.as_view(), name='statement-dispute'),
    path('sales/', SaleRecordListView.as_view(), name='sale-records'),
    path('services/', WebServiceListView.as_view(), name='service-list'),
    path('services/<int:service_id>/activate/', SellerActivateServiceView.as_view(), name='seller-activate-service'),
    path('charges/', SellerChargesListView.as_view(), name='seller-charges'),
    path('codes/apply/', ApplyDiscountCodeView.as_view(), name='apply-code'),
    path('codes/', SellerActiveCodesView.as_view(), name='seller-codes'),

    # Admin
    path('admin/statements/', AdminStatementListView.as_view(), name='admin-statement-list'),
    path('admin/statements/generate/', StatementGenerateView.as_view(), name='statement-generate'),
    path('admin/statements/calculate/', StatementCalculateView.as_view(), name='statement-calculate'),
    path('admin/statements/<int:pk>/', AdminStatementDetailView.as_view(), name='admin-statement-detail'),
    path('admin/statements/<int:pk>/send/', StatementSendView.as_view(), name='statement-send'),
    path('admin/statements/<int:pk>/mark-paid/', StatementMarkPaidView.as_view(), name='statement-mark-paid'),
    path('admin/statements/<int:pk>/line-items/', StatementLineItemListCreateView.as_view(), name='statement-line-items'),
    path('admin/statements/<int:statement_id>/line-items/<int:pk>/', StatementLineItemDetailView.as_view(), name='statement-line-item-detail'),
    path('admin/statements/<int:pk>/disputes/<int:dispute_id>/resolve/', AdminStatementDisputeResolveView.as_view(), name='statement-dispute-resolve'),
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