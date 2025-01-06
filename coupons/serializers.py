from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Coupon


class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'description',
            'discount_amount',
            'discount_type',
            'allowed_users',
            'max_uses',
            'uses',
            'allowed_outlets',
            'all_users_allowed',
            'all_outlets_allowed',
            'effective_at',
            'expires_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'uses',]
        
    def validate(self, data):
        if data.get('discount_type') == 'PERCENTAGE' and data.get('discount_amount') > 100:
            raise serializers.ValidationError("Percentage discount cannot exceed 100%")
        return data
