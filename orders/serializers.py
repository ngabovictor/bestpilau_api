from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Order, OrderStatusTracker


class OrderStatusTrackerSerializer(ModelSerializer):
    class Meta:
        model = OrderStatusTracker
        fields = ['id', 'status', 'created_at']
        read_only_fields = ['created_at']


class OrderSerializer(ModelSerializer):
    status_history = OrderStatusTrackerSerializer(source='orderstatustracker_set', many=True, read_only=True)
    customer = serializers.SerializerMethodField()
    assigned_rider = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'reference_code', 
            'outlet',
            'customer',
            'delivery_address',
            'assigned_rider',
            'products',
            'total_amount',
            'status',
            'notes',
            'estimated_completion_time',
            'coupon',
            'fees_breakdown',
            'status_history',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['reference_code', 'created_at', 'updated_at']

    def get_customer(self, obj):
        return {
            'id': obj.customer.id,
            'username': obj.customer.username,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name
        }

    def get_assigned_rider(self, obj):
        if obj.assigned_rider:
            return {
                'id': obj.assigned_rider.id,
                'username': obj.assigned_rider.username,
                'first_name': obj.assigned_rider.first_name,
                'last_name': obj.assigned_rider.last_name
            }
        return None

    def validate(self, data):
        if data.get('total_amount', 0) < 0:
            raise serializers.ValidationError("Total amount cannot be negative")
        return data
