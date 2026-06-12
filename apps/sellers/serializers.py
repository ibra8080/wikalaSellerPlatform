from rest_framework import serializers
from .models import SellerProfile, SellerDocument, SellerTier, Promotion, SellerPromotion


class SellerProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = SellerProfile
        fields = (
            'id', 'email', 'seller_id', 'full_name', 'business_name',
            'profile_pic_url', 'bio', 'phone', 'whatsapp',
            'country', 'city', 'seller_tier', 'status',
            'rejection_reason', 'approved_at', 'created_at',
            'exported_before', 'referral_source',
            'legal_company_name', 'tax_id', 'commercial_register_no', 'legal_address',
            'bank_account_holder', 'bank_name', 'bank_iban', 'bank_swift',
        )
        read_only_fields = (
            'id', 'seller_id', 'approved_at', 'created_at'
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
        profile, created = SellerProfile.objects.get_or_create(
            user=user,
            defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(profile, attr, value)
            profile.save()
        return profile


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