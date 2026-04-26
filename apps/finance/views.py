from rest_framework import generics, permissions
from .models import FeeStructure, SellerStatement, SaleRecord
from .serializers import FeeStructureSerializer, SellerStatementSerializer, SaleRecordSerializer
from apps.sellers.views import IsSeller, IsAdmin


class FeeStructureView(generics.ListAPIView):
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = FeeStructure.objects.filter(is_active=True)


# Seller: view their statements
class SellerStatementListView(generics.ListAPIView):
    serializer_class = SellerStatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return SellerStatement.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-period_end')


class SellerStatementDetailView(generics.RetrieveAPIView):
    serializer_class = SellerStatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return SellerStatement.objects.filter(
            seller=self.request.user.seller_profile
        )


# Seller: view their sale records
class SaleRecordListView(generics.ListAPIView):
    serializer_class = SaleRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return SaleRecord.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-sale_date')


# Admin: manage statements
class AdminStatementListView(generics.ListCreateAPIView):
    serializer_class = SellerStatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerStatement.objects.all().order_by('-period_end')


class AdminStatementDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerStatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerStatement.objects.all()


# Admin: manage sale records
class AdminSaleRecordCreateView(generics.CreateAPIView):
    serializer_class = SaleRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
        serializer.save(seller=serializer.validated_data['product'].seller)