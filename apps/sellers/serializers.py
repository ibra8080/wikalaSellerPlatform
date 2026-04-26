from rest_framework import serializers
from .models import SellerProfile, SellerDocument, SellerTier, Promotion, SellerPromotion


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = (
            'id', 'seller_id', 'full_name', 'business_name',
            'profile_pic_url', 'bio', 'phone', 'whatsapp',
            'country', 'city', 'seller_tier', 'status',
            'rejection_reason', 'exported_before', 'referral_source',
            'approved_at', 'created_at'
        )
        read_only_fields = (
            'id', 'seller_id', 'status', 'rejection_reason',
            'approved_at', 'created_at'
        )


class SellerRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = (
            'full_name', 'business_name', 'phone', 'whatsapp',
            'country', 'city', 'bio', 'exported_before', 'referral_source'
        )

    def create(self, validated_data):
        user = self.context['request'].user
        return SellerProfile.objects.create(user=user, **validated_data)


class SellerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDocument
        fields = ('id', 'doc_type', 'file_url', 'verified', 'uploaded_at')
        read_only_fields = ('id', 'verified', 'uploaded_at')


class SellerTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerTier
        fields = ('id', 'name', 'description')


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'


class SellerPromotionSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)

    class Meta:
        model = SellerPromotion
        fields = ('id', 'promotion', 'assigned_at', 'expires_at', 'is_active')