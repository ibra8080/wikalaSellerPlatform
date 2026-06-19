from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Product, ProductVariant, ProductImage, Certification, ProductPromotion, Category
from .serializers import (
    ProductSerializer, ProductCreateSerializer, CategorySerializer,
    ProductVariantSerializer, CertificationSerializer, ProductPromotionSerializer,
    ProductImageSerializer
)
from apps.sellers.views import IsSeller, IsAdmin
from utils.cloudinary import upload_image
from utils.email import send_product_approved, send_product_rejected


# Fields that a seller is NOT allowed to change directly
SELLER_PROTECTED_FIELDS = {'rejection_reason', 'previous_status',
                           'shopify_product_id', 'approved_at', 'listed_at'}

# Fields that trigger re-review when changed on an active product
NEEDS_REVIEW_FIELDS = {'price', 'name_ar', 'name_en', 'name_de'}


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.filter(parent=None)


# ──────────────────────────────────────
# Seller: Products
# ──────────────────────────────────────

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-created_at')


class ProductDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user.seller_profile)

    def perform_update(self, serializer):
        instance = self.get_object()
        data = self.request.data

        # Seller can only change status: draft → pending_review
        new_status = data.get('status')
        if new_status:
            if not (instance.status == 'draft' and new_status == 'pending_review'):
                data.pop('status', None)

        # Strip protected fields — seller cannot change these
        for field in SELLER_PROTECTED_FIELDS:
            if field in data:
                data.pop(field, None)

        # Check if seller is editing a sensitive field on an active product
        has_sensitive_change = bool(NEEDS_REVIEW_FIELDS & set(data.keys()))

        active_statuses = [
            'approved', 'listed', 'in_warehouse_germany',
            'in_transit', 'in_warehouse_egypt', 'awaiting_seller_shipment'
        ]

        if has_sensitive_change and instance.status in active_statuses:
            serializer.save(
                status='pending_review',
                previous_status=instance.status
            )
        else:
            serializer.save()


# ──────────────────────────────────────
# Admin: Products
# ──────────────────────────────────────

class AdminProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all().order_by('-created_at')


class AdminProductDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = self.request.data.get('status')

        if new_status == 'approved' and instance.previous_status:
            # Re-approving after re-review: restore previous status
            serializer.save(
                status=instance.previous_status,
                previous_status=''
            )
            send_product_approved(instance)
            for variant in instance.variants.filter(sku__isnull=True):
                variant.save()
        elif new_status == 'approved' and not instance.previous_status:
            # First-time approval
            instance_updated = serializer.save(status='approved')
            instance_updated.approved_at = timezone.now()
            instance_updated.save()
            send_product_approved(instance_updated)
            for variant in instance_updated.variants.filter(sku__isnull=True):
                variant.save()
            self._create_listing_charge(instance_updated)
        elif new_status == 'rejected':
            serializer.save()
            send_product_rejected(instance)
        else:
            serializer.save()

    def _create_listing_charge(self, product):
        from apps.finance.models import WebService, WebServiceCharge
        from decimal import Decimal
        try:
            service = WebService.objects.filter(
                level='product', mandatory=True, is_active=True
            ).first()
            if not service:
                return
            if WebServiceCharge.objects.filter(
                seller=product.seller, service=service, product=product
            ).exists():
                return

            # حساب السعر حسب عدد الفاريانتس
            variant_count = product.variants.count()
            base_price = service.price  # €2.00
            extra_variants = max(0, variant_count - 4)
            extra_charge = Decimal(str(extra_variants)) * Decimal('0.50')
            final_price = base_price + extra_charge

            WebServiceCharge.objects.create(
                seller=product.seller,
                service=service,
                product=product,
                original_price=final_price,
                discount_amount=Decimal('0'),
                final_price=final_price,
                status='pending',
            )
        except Exception:
            pass


class AdminProductDeleteView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all()


# ──────────────────────────────────────
# Seller: Product Variants
# ──────────────────────────────────────

class ProductVariantView(generics.ListCreateAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ProductVariant.objects.filter(
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )

    def perform_create(self, serializer):
        product = get_object_or_404(
            Product,
            id=self.kwargs['pk'],
            seller=self.request.user.seller_profile
        )
        serializer.save(product=product)


class ProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return get_object_or_404(
            ProductVariant,
            id=self.kwargs['variant_pk'],
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )


# ──────────────────────────────────────
# Seller: Product Promotions
# ──────────────────────────────────────

class ProductPromotionView(generics.ListCreateAPIView):
    serializer_class = ProductPromotionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ProductPromotion.objects.filter(
            seller=self.request.user.seller_profile
        )

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)


# ──────────────────────────────────────
# Seller: Product Images
# ──────────────────────────────────────

class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        product = get_object_or_404(
            Product,
            id=pk,
            seller=request.user.seller_profile
        )
        file = request.FILES.get('image')
        if not file:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type
        ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
        if file.content_type not in ALLOWED_TYPES:
            return Response(
                {'error': 'Invalid file type. Allowed: JPG, PNG, WebP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size (5MB max)
        MAX_SIZE = 5 * 1024 * 1024
        if file.size > MAX_SIZE:
            return Response(
                {'error': 'File too large. Maximum size is 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate max images per product (10)
        if product.images.count() >= 10:
            return Response(
                {'error': 'Maximum 10 images per product.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = upload_image(file, folder='products')
        is_primary = not product.images.exists()
        image = ProductImage.objects.create(
            product=product,
            image_url=url,
            is_primary=is_primary,
            order=product.images.count()
        )
        return Response(
            ProductImageSerializer(image).data,
            status=status.HTTP_201_CREATED
        )


class ProductImageDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return get_object_or_404(
            ProductImage,
            id=self.kwargs['image_pk'],
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )


# ============================================================
# Shopify CSV Export
# ============================================================
import csv
import re
from django.http import HttpResponse


def _slugify_handle(product_code):
    handle = (product_code or '').lower().strip()
    handle = re.sub(r'[^a-z0-9]+', '-', handle)
    return handle.strip('-')


SHOPIFY_CSV_COLUMNS = [
    'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published',
    'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value',
    'Option3 Name', 'Option3 Value',
    'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker',
    'Variant Inventory Qty', 'Variant Inventory Policy',
    'Variant Fulfillment Service', 'Variant Price', 'Variant Compare-at Price',
    'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode',
    'Image Src', 'Image Alt Text',
]


class ShopifyExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="wikala_shopify_export.csv"'
        response.write('﻿')

        writer = csv.writer(response)
        writer.writerow(SHOPIFY_CSV_COLUMNS)

        products = (
            Product.objects
            .filter(status__in=['listed', 'approved'])
            .prefetch_related('variants__inventory', 'images', 'seller')
            .order_by('product_code')
        )

        # Filter by specific IDs if provided (?ids=3,8)
        ids_param = request.query_params.get('ids')
        if ids_param:
            try:
                id_list = [int(i) for i in ids_param.split(',') if i.strip()]
                products = products.filter(id__in=id_list)
            except ValueError:
                pass

        for product in products:
            handle = _slugify_handle(product.product_code)
            vendor = f"Wikala - {product.seller.business_name}" if product.seller else "Wikala"
            body = product.description_en or ''
            category_name = product.category.name_en if product.category else ''
            price = str(product.price)

            variants = [v for v in product.variants.all() if v.sku and v.sku.strip()]

            images = sorted(
                product.images.all(),
                key=lambda im: (not im.is_primary, im.order or 0)
            )
            image_urls = [im.image_url for im in images if im.image_url]

            if not variants:
                continue

            has_variants = not (len(variants) == 1 and not variants[0].color and not variants[0].size)

            first_row = True
            img_index = 0

            for v in variants:
                try:
                    qty = v.inventory.quantity_in_germany
                except Exception:
                    qty = 0

                if has_variants:
                    opt1_name, opt1_val = 'Color', (v.color or '-')
                    opt2_name, opt2_val = ('Size', v.size) if v.size else ('', '')
                else:
                    opt1_name, opt1_val = 'Title', 'Default Title'
                    opt2_name, opt2_val = '', ''

                row = {
                    'Handle': handle,
                    'Title': product.name_en if first_row else '',
                    'Body (HTML)': body if first_row else '',
                    'Vendor': vendor if first_row else '',
                    'Type': category_name if first_row else '',
                    'Tags': '',
                    'Published': 'TRUE' if first_row else '',
                    'Option1 Name': opt1_name,
                    'Option1 Value': opt1_val,
                    'Option2 Name': opt2_name,
                    'Option2 Value': opt2_val,
                    'Option3 Name': '',
                    'Option3 Value': '',
                    'Variant SKU': v.sku,
                    'Variant Grams': int((product.unit_weight_kg or 0) * 1000),
                    'Variant Inventory Tracker': 'shopify',
                    'Variant Inventory Qty': qty,
                    'Variant Inventory Policy': 'deny',
                    'Variant Fulfillment Service': 'manual',
                    'Variant Price': price,
                    'Variant Compare-at Price': '',
                    'Variant Requires Shipping': 'TRUE',
                    'Variant Taxable': 'TRUE',
                    'Variant Barcode': v.external_barcode or '',
                    'Image Src': image_urls[img_index] if img_index < len(image_urls) else '',
                    'Image Alt Text': product.name_en if img_index < len(image_urls) else '',
                }
                writer.writerow([row[col] for col in SHOPIFY_CSV_COLUMNS])
                first_row = False
                if img_index < len(image_urls):
                    img_index += 1

            while img_index < len(image_urls):
                extra = {col: '' for col in SHOPIFY_CSV_COLUMNS}
                extra['Handle'] = handle
                extra['Image Src'] = image_urls[img_index]
                extra['Image Alt Text'] = product.name_en
                writer.writerow([extra[col] for col in SHOPIFY_CSV_COLUMNS])
                img_index += 1

        return response