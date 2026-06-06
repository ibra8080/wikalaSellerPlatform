from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    FeeStructure, SellerStatement, SaleRecord,
    WebService, DiscountCode, SellerDiscountCode,
    SellerDiscount, WebServiceCharge
)
from .serializers import (
    FeeStructureSerializer, SellerStatementSerializer, SaleRecordSerializer,
    WebServiceSerializer, DiscountCodeSerializer, SellerDiscountCodeSerializer,
    SellerDiscountSerializer, WebServiceChargeSerializer
)
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
        serializer.save(seller=serializer.validated_data['variant'].product.seller)


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
        ).select_related('variant', 'variant__product')

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

class SellerActivateServiceView(APIView):
    """Seller: ينشئ فاتورة على نفسه لخدمة اختيارية"""
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def post(self, request, service_id):
        from apps.finance.models import WebService, WebServiceCharge, SellerDiscount, SellerDiscountCode

        try:
            service = WebService.objects.get(id=service_id, is_active=True)
        except WebService.DoesNotExist:
            return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

        seller = request.user.seller_profile

        # Check if already charged
        if WebServiceCharge.objects.filter(seller=seller, service=service).exists():
            return Response({'error': 'Service already activated'}, status=status.HTTP_400_BAD_REQUEST)

        original_price = service.price
        discount_amount = Decimal('0')

        # Direct discount
        direct = SellerDiscount.objects.filter(
            seller=seller, service=service, is_active=True
        ).first()
        if direct:
            if direct.discount_type == 'percent':
                discount_amount = original_price * direct.value / 100
            else:
                discount_amount = direct.value

        # Code discount
        code_usage = SellerDiscountCode.objects.filter(
            seller=seller, code__is_active=True
        ).select_related('code').first()
        if code_usage and code_usage.code.is_valid():
            code = code_usage.code
            if code.applies_to == 'all' or code.service == service:
                if code.discount_type == 'percent':
                    code_disc = original_price * code.value / 100
                else:
                    code_disc = code.value
                discount_amount = max(discount_amount, code_disc)

        final_price = max(Decimal('0'), original_price - discount_amount)

        charge = WebServiceCharge.objects.create(
            seller=seller,
            service=service,
            original_price=original_price,
            discount_amount=discount_amount,
            final_price=final_price,
            status='waived' if final_price == 0 else 'pending',
        )
        return Response(WebServiceChargeSerializer(charge).data, status=status.HTTP_201_CREATED)


# ── WebService ────────────────────────────────────────────────────────────────

class WebServiceListView(generics.ListAPIView):
    """Seller: يشوف الخدمات المتاحة"""
    serializer_class = WebServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WebService.objects.filter(is_active=True)


class AdminWebServiceListCreateView(generics.ListCreateAPIView):
    """Admin: يدير الخدمات"""
    serializer_class = WebServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = WebService.objects.all().order_by('-created_at')


class AdminWebServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: يعدل أو يحذف خدمة"""
    serializer_class = WebServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = WebService.objects.all()


# ── DiscountCode ──────────────────────────────────────────────────────────────

class AdminDiscountCodeListCreateView(generics.ListCreateAPIView):
    """Admin: يدير أكواد الخصم"""
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = DiscountCode.objects.all().order_by('-created_at')


class AdminDiscountCodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: يعدل أو يحذف كود"""
    serializer_class = DiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = DiscountCode.objects.all()


class ApplyDiscountCodeView(APIView):
    """Seller: يطبق كود خصم"""
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def post(self, request):
        code_str = request.data.get('code', '').strip().upper()
        if not code_str:
            return Response(
                {'error': 'Code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            code = DiscountCode.objects.get(code=code_str)
        except DiscountCode.DoesNotExist:
            return Response(
                {'error': 'Invalid code'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not code.is_valid():
            return Response(
                {'error': 'Code is expired or inactive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        seller = request.user.seller_profile

        # تحقق مش استخدمه قبل كده
        if SellerDiscountCode.objects.filter(seller=seller, code=code).exists():
            return Response(
                {'error': 'You have already used this code'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # طبق الكود
        SellerDiscountCode.objects.create(seller=seller, code=code)
        code.used_count += 1
        code.save()

        return Response({
            'success': True,
            'message': f'Code "{code.code}" applied successfully',
            'discount_type': code.discount_type,
            'value': float(code.value),
            'applies_to': code.applies_to,
        })


class SellerActiveCodesView(generics.ListAPIView):
    """Seller: يشوف الأكواد المطبقة عليه"""
    serializer_class = SellerDiscountCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return SellerDiscountCode.objects.filter(
            seller=self.request.user.seller_profile
        ).select_related('code')


# ── SellerDiscount ────────────────────────────────────────────────────────────

class AdminSellerDiscountListCreateView(generics.ListCreateAPIView):
    """Admin: يضيف خصم مباشر على بائع"""
    serializer_class = SellerDiscountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerDiscount.objects.all().order_by('-created_at')


class AdminSellerDiscountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: يعدل أو يحذف خصم مباشر"""
    serializer_class = SellerDiscountSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerDiscount.objects.all()


# ── WebServiceCharge ──────────────────────────────────────────────────────────

class SellerChargesListView(generics.ListAPIView):
    """Seller: يشوف فواتير الخدمات بتاعته"""
    serializer_class = WebServiceChargeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return WebServiceCharge.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-created_at')


class AdminChargesListCreateView(generics.ListCreateAPIView):
    """Admin: يدير فواتير الخدمات"""
    serializer_class = WebServiceChargeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = WebServiceCharge.objects.all().order_by('-created_at')


class AdminChargeDetailView(generics.RetrieveUpdateAPIView):
    """Admin: يعدل فاتورة (مثلاً يغير status لـ paid)"""
    serializer_class = WebServiceChargeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = WebServiceCharge.objects.all()


class AdminCreateRegistrationChargeView(APIView):
    """Admin: ينشئ فاتورة تسجيل على بائع تلقائياً"""
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request, seller_id):
        from apps.sellers.models import SellerProfile

        try:
            seller = SellerProfile.objects.get(id=seller_id)
        except SellerProfile.DoesNotExist:
            return Response({'error': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)

        # جيب خدمة التسجيل
        try:
            service = WebService.objects.get(type='one_time', mandatory=True, is_active=True)
        except WebService.DoesNotExist:
            return Response({'error': 'Registration service not found'}, status=status.HTTP_404_NOT_FOUND)

        # تحقق مش عنده فاتورة تسجيل قبل كده
        if WebServiceCharge.objects.filter(seller=seller, service=service).exists():
            return Response({'error': 'Registration charge already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # احسب الخصم
        original_price  = service.price
        discount_amount = Decimal('0')

        # خصم مباشر من الأدمن
        direct_discount = SellerDiscount.objects.filter(
            seller=seller, service=service, is_active=True
        ).first()
        if direct_discount:
            if direct_discount.discount_type == 'percent':
                discount_amount = original_price * direct_discount.value / 100
            else:
                discount_amount = direct_discount.value

        # كود خصم
        code_usage = SellerDiscountCode.objects.filter(
            seller=seller,
            code__applies_to__in=['all', 'specific'],
        ).filter(
            code__is_active=True
        ).select_related('code').first()

        if code_usage and code_usage.code.is_valid():
            code = code_usage.code
            if code.applies_to == 'all' or code.service == service:
                if code.discount_type == 'percent':
                    code_discount = original_price * code.value / 100
                else:
                    code_discount = code.value
                discount_amount = max(discount_amount, code_discount)

        final_price = max(Decimal('0'), original_price - discount_amount)

        charge = WebServiceCharge.objects.create(
            seller=seller,
            service=service,
            original_price=original_price,
            discount_amount=discount_amount,
            final_price=final_price,
            status='waived' if final_price == 0 else 'pending',
        )

        return Response(WebServiceChargeSerializer(charge).data, status=status.HTTP_201_CREATED)