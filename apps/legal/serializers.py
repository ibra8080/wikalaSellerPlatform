from rest_framework import serializers
from .models import WiderrufRequest


class WiderrufRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WiderrufRequest
        fields = ('id', 'name', 'email', 'bestellnummer', 'widerrufserklaerung', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name ist erforderlich.")
        return value.strip()

    def validate_bestellnummer(self, value):
        if not value.strip():
            raise serializers.ValidationError("Bestellnummer ist erforderlich.")
        return value.strip()