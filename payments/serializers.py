from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Transaction


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id',
            'reference_code',
            'order',
            'outlet',
            'amount',
            'currency',
            'status',
            'payment_method',
            'payment_account_number',
            'gw_codename',
            'transaction_type',
            'reference_id',
            'error_message',
            'refund_status',
            'refunded_amount',
            'gw_request_payload',
            'gw_request_response',
            'gw_request_callback',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['reference_code', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('amount', 0) <= 0:
            raise serializers.ValidationError("Transaction amount must be greater than 0")
        
        if data.get('refunded_amount', 0) > data.get('amount', 0):
            raise serializers.ValidationError("Refunded amount cannot exceed transaction amount")

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['order'] = {
            'id': instance.order.id,
            'reference_code': instance.order.reference_code
        }
        return representation
