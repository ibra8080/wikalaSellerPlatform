from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import FeeStructure, SellerStatement, SaleRecord
from .serializers import FeeStructureSerializer, SellerStatementSerializer, SaleRecordSerializer
from apps.sellers.views import IsSeller, IsAdmin
from apps.inventory.models import VariantInventory
from apps.products.models import Product
from decimal import Decimal
import datetime


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


class StatementCalculateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        seller_id     = request.data.get('seller')
        period_start  = request.data.get('period_start')
        period_end    = request.data.get('period_end')
        shipping_rate = Decimal(str(request.data.get('shipping_rate', '0')))

        if not all([seller_id, period_start, period_end]):
            return Response(
                {'error': 'seller, period_start, period_end required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fee = FeeStructure.objects.filter(is_active=True).first()
        if not fee:
            return Response(
                {'error': 'No active fee structure found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        period_start_date = datetime.date.fromisoformat(period_start)
        period_end_date   = datetime.date.fromisoformat(period_end)

        sale_records = SaleRecord.objects.filter(
            seller_id=seller_id,
            sale_date__gte=period_start_date,
            sale_date__lte=period_end_date,
        ).select_related('product')

        inventories = VariantInventory.objects.filter(
            variant__product__seller_id=seller_id,
            quantity_in_germany__gt=0,
        ).select_related('variant__product')

        total_sales       = Decimal('0')
        commission_amount = Decimal('0')
        pick_pack_amount  = Decimal('0')
        storage_amount    = Decimal('0')
        breakdown         = []

        for rec in sale_records:
            total_sales       += rec.total_amount
            commission_amount += (rec.unit_price * fee.commission_wikala + Decimal('1')) * rec.quantity_sold
            pick_pack_amount  += fee.pick_pack_fee * rec.quantity_sold

        now = datetime.datetime.now()
        for inv in inventories:
            product = inv.variant.product
            if not inv.arrived_germany_at:
                continue
            arrived = inv.arrived_germany_at
            if hasattr(arrived, 'date'):
                arrived = arrived.replace(tzinfo=None)
            days    = (now - arrived).days
            months  = Decimal(str(days)) / Decimal('30')

            l = Decimal(str(product.carton_length_cm or 0)) / 100
            w = Decimal(str(product.carton_width_cm or 0)) / 100
            h = Decimal(str(product.carton_height_cm or 0)) / 100
            volume_m3 = l * w * h * Decimal('1.15')

            units_per_carton = product.units_per_carton or 1
            num_cartons = Decimal(str(inv.quantity_in_germany)) / Decimal(str(units_per_carton))

            sku_storage = fee.storage_fee_per_cbm * volume_m3 * num_cartons * months
            storage_amount += sku_storage

            breakdown.append({
                'product_code': product.product_code,
                'product_name': product.name_en,
                'sku':          inv.variant.sku,
                'qty_germany':  inv.quantity_in_germany,
                'months':       round(float(months), 2),
                'volume_m3':    round(float(volume_m3), 4),
                'storage_cost': round(float(sku_storage), 2),
            })

        shipping_amount = Decimal('0')
        shipping_detail = []

        products_for_seller = Product.objects.filter(
            seller_id=seller_id,
            status__in=['in_transit', 'in_warehouse_germany', 'listed']
        )

        for product in products_for_seller:
            if not all([
                product.carton_weight_kg,
                product.carton_length_cm,
                product.carton_width_cm,
                product.carton_height_cm,
                product.units_per_carton,
            ]):
                continue

            vol_weight = (
                Decimal(str(product.carton_length_cm)) *
                Decimal(str(product.carton_width_cm)) *
                Decimal(str(product.carton_height_cm))
            ) / Decimal('5000')

            actual_weight = Decimal(str(product.carton_weight_kg))
            chargeable    = max(actual_weight, vol_weight)

            total_units = sum(
                inv.quantity_in_germany
                for inv in inventories
                if inv.variant.product_id == product.id
            )
            if total_units == 0:
                continue

            num_cartons      = Decimal(str(total_units)) / Decimal(str(product.units_per_carton))
            product_shipping = chargeable * num_cartons * shipping_rate

            shipping_amount += product_shipping
            shipping_detail.append({
                'product_code':  product.product_code,
                'product_name':  product.name_en,
                'actual_kg':     float(actual_weight),
                'volumetric_kg': round(float(vol_weight), 3),
                'chargeable_kg': round(float(chargeable), 3),
                'num_cartons':   round(float(num_cartons), 2),
                'shipping_cost': round(float(product_shipping), 2),
            })

        net_amount = total_sales - commission_amount - storage_amount - pick_pack_amount - shipping_amount

        return Response({
            'total_sales':         round(float(total_sales), 2),
            'commission_amount':   round(float(commission_amount), 2),
            'storage_fee_amount':  round(float(storage_amount), 2),
            'pick_pack_amount':    round(float(pick_pack_amount), 2),
            'shipping_fee_amount': round(float(shipping_amount), 2),
            'net_amount':          round(float(net_amount), 2),
            'breakdown':           breakdown,
            'shipping_detail':     shipping_detail,
        })