from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
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


class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.filter(parent=None)


# Seller: list and create products
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


# Seller: view/update a specific product
class ProductDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user.seller_profile)

    def perform_update(self, serializer):
        instance = self.get_object()
        data = self.request.data

        needs_review_fields = {'price', 'name_ar', 'name_en', 'name_de'}
        has_sensitive_change = bool(needs_review_fields & set(data.keys()))

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


# Admin: list all products
class AdminProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all().order_by('-created_at')


# Admin: view/update any product (approve/reject)
class AdminProductDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = self.request.data.get('status')

        if new_status == 'approved' and instance.previous_status:
            serializer.save(
                status=instance.previous_status,
                previous_status=''
            )
            send_product_approved(instance)
        elif new_status == 'approved' and not instance.previous_status:
            instance_updated = serializer.save(status='approved')
            instance_updated.approved_at = timezone.now()
            instance_updated.save()
            send_product_approved(instance_updated)
        elif new_status == 'rejected':
            serializer.save()
            send_product_rejected(instance)
        else:
            serializer.save()


# Seller: manage product variants
class ProductVariantView(generics.ListCreateAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ProductVariant.objects.filter(
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )

    def perform_create(self, serializer):
        product = Product.objects.get(
            id=self.kwargs['pk'],
            seller=self.request.user.seller_profile
        )
        serializer.save(product=product)


# Seller: manage promotions on their products
class ProductPromotionView(generics.ListCreateAPIView):
    serializer_class = ProductPromotionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ProductPromotion.objects.filter(
            seller=self.request.user.seller_profile
        )

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)


class ProductImageUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        product = Product.objects.get(
            id=pk,
            seller=request.user.seller_profile
        )
        file = request.FILES.get('image')
        if not file:
            return Response(
                {'error': 'No image provided'},
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


class ProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ProductVariant.objects.filter(
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )

    def get_object(self):
        return ProductVariant.objects.get(
            id=self.kwargs['variant_pk'],
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )


class ProductImageDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return ProductImage.objects.get(
            id=self.kwargs['image_pk'],
            product__id=self.kwargs['pk'],
            product__seller=self.request.user.seller_profile
        )


class AdminProductDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Product.objects.all()