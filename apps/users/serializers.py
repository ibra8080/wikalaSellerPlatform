import unicodedata

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


def clean_text(value):
    """Strip whitespace and remove invisible/directional control chars
    (RTL/LTR marks, zero-width chars) that mobile/Arabic keyboards inject."""
    if not isinstance(value, str):
        return value
    # Remove Unicode 'format' category chars (Cf) — RLM, LRM, ZWSP, embeds, etc.
    value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Cf')
    return value.strip()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=User.Role.SELLER
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role', 'is_active', 'date_joined')
        read_only_fields = ('id', 'role', 'is_active', 'date_joined')


from django.db import transaction
from apps.sellers.models import SellerProfile


class FullRegisterSerializer(serializers.Serializer):
    # User fields
    email = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    # Seller fields
    full_name = serializers.CharField()
    business_name = serializers.CharField()
    phone = serializers.CharField(allow_blank=True, required=False)
    whatsapp = serializers.CharField(allow_blank=True, required=False)
    country = serializers.CharField(allow_blank=True, required=False)
    city = serializers.CharField(allow_blank=True, required=False)
    exported_before = serializers.BooleanField(required=False, default=False)
    referral_source = serializers.CharField(allow_blank=True, required=False)

    def validate_email(self, value):
        value = clean_text(value).lower()
        from django.core.validators import validate_email as dj_validate_email
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            dj_validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError('Enter a valid email address.')
        return value

    def validate_username(self, value):
        return clean_text(value)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'This email is already registered.'})
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'This username is already taken.'})
        if SellerProfile.objects.filter(business_name=attrs['business_name']).exists():
            raise serializers.ValidationError({'business_name': 'This business name is already taken.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=User.Role.SELLER,
        )
        seller = SellerProfile.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            business_name=validated_data['business_name'],
            phone=validated_data.get('phone', ''),
            whatsapp=validated_data.get('whatsapp', ''),
            country=validated_data.get('country', ''),
            city=validated_data.get('city', ''),
            exported_before=validated_data.get('exported_before', False),
            referral_source=validated_data.get('referral_source', ''),
        )
        from utils.email import send_seller_registration_received
        send_seller_registration_received(seller)
        return user

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'email': instance.email,
            'username': instance.username,
            'message': 'Registration successful',
        }