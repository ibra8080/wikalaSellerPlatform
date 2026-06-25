from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant, Certification, ProductPromotion, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name_ar', 'name_en', 'name_de', 'parent')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image_url', 'is_primary', 'order')


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ('id', 'color', 'size', 'sku', 'external_barcode', 'quantity_submitted')
        read_only_fields = ('sku',)


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ('id', 'type', 'file_url', 'uploaded_at')
        read_only_fields = ('uploaded_at',)


class ProductPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPromotion
        fields = ('id', 'promo_type', 'value', 'start_date', 'end_date', 'is_active')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'product_code', 'seller', 'seller_name',
            'name_ar', 'name_en', 'name_de',
            'description_ar', 'description_en', 'description_de',
            'marketing_desc_ar', 'marketing_desc_en', 'marketing_desc_de',
            'materials', 'brand_name', 'model_number', 'custom_specs',
            'keywords', 'category', 'price', 'production_cost',
            'unit_weight_kg', 'unit_length_cm', 'unit_width_cm', 'unit_height_cm',
            'units_per_carton', 'carton_weight_kg',
            'carton_length_cm', 'carton_width_cm', 'carton_height_cm',
            'has_care_label', 'status', 'rejection_reason', 'previous_status',
            'shopify_product_id', 'approved_at', 'listed_at', 'created_at',
            'images', 'variants', 'certifications'
        )
        read_only_fields = (
            'product_code', 'seller',
            'shopify_product_id', 'approved_at', 'listed_at', 'created_at'
        )


class ProductCreateSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_de = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name_ar', 'name_en', 'name_de',
            'description_ar', 'description_en', 'description_de',
            'marketing_desc_ar', 'marketing_desc_en', 'marketing_desc_de',
            'materials', 'brand_name', 'model_number', 'custom_specs',
            'keywords', 'category', 'price', 'production_cost',
            'unit_weight_kg', 'unit_length_cm', 'unit_width_cm', 'unit_height_cm',
            'units_per_carton', 'carton_weight_kg',
            'carton_length_cm', 'carton_width_cm', 'carton_height_cm',
            'has_care_label', 'variants', 'images', 'certifications'
        )

    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        images_data = validated_data.pop('images', [])
        certifications_data = validated_data.pop('certifications', [])

        seller = self.context['request'].user.seller_profile
        product = Product.objects.create(seller=seller, **validated_data)

        for variant in variants_data:
            ProductVariant.objects.create(product=product, **variant)

        for image in images_data:
            ProductImage.objects.create(product=product, **image)

        for cert in certifications_data:
            Certification.objects.create(product=product, **cert)

        return product