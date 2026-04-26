from rest_framework import generics, permissions
from .models import Contract, ShippingFeeOption
from .serializers import ContractSerializer, ShippingFeeOptionSerializer
from apps.sellers.views import IsSeller, IsAdmin


# Seller: view their contracts
class SellerContractListView(generics.ListAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return Contract.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-created_at')


class SellerContractDetailView(generics.RetrieveAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return Contract.objects.filter(
            seller=self.request.user.seller_profile
        )


# Admin: full contract management
class AdminContractListCreateView(generics.ListCreateAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Contract.objects.all().order_by('-created_at')


class AdminContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Contract.objects.all()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                'Only Wikala Admin can delete contracts.'
            )
        instance.delete()


# ShippingFeeOption
class ShippingFeeOptionView(generics.ListCreateAPIView):
    serializer_class = ShippingFeeOptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShippingFeeOption.objects.filter(
            product__seller=self.request.user.seller_profile
        )


class ShippingFeeOptionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ShippingFeeOptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShippingFeeOption.objects.filter(
            product__seller=self.request.user.seller_profile
        )