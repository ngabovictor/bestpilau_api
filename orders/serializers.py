from rest_framework import serializers
from authentication.models import User
from utils.serializers import ModelSerializer
from .models import Order, OrderStatusTracker


class OrderStatusTrackerSerializer(ModelSerializer):
    class Meta:
        model = OrderStatusTracker
        fields = ['id', 'status', 'created_at']
        read_only_fields = ['created_at']


class OrderSerializer(ModelSerializer):
    status_history = OrderStatusTrackerSerializer(source='orderstatustracker_set', many=True, read_only=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=False, queryset=User.objects.all(), allow_null=False)
    assigned_rider = serializers.PrimaryKeyRelatedField(read_only=False, queryset=User.objects.filter(is_rider=True), allow_null=True)

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
            'cancelled_reason',
            'estimated_completion_time',
            'coupon',
            'fees_breakdown',
            'status_history',
            'created_at',
            'updated_at',
            'created_by'
        ]
        read_only_fields = ['reference_code', 'created_at', 'updated_at', 'created_by']

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        
        representation['customer'] = {
            'id': str(obj.customer.id),
            'username': obj.customer.username,
            'first_name': obj.customer.first_name,
            'last_name': obj.customer.last_name
        }

        if obj.assigned_rider:
            representation['assigned_rider'] = {
                'id': str(obj.assigned_rider.id),
                'username': obj.assigned_rider.username,
                'first_name': obj.assigned_rider.first_name,
                'last_name': obj.assigned_rider.last_name
            }
        
        # Add payment status based on successful transactions
        representation['is_paid'] = obj.transactions.filter(status='COMPLETED').exists()
        representation['outlet'] = str(obj.outlet.id)
        representation['created_by'] = str(obj.created_by.id)
        representation['created_by'] = str(obj.created_by.id)
        
        return representation

    def validate(self, data):
        if data.get('total_amount', 0) < 0:
            raise serializers.ValidationError("Total amount cannot be negative")
        return data
    
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context.get('request').user
        coupon = validated_data.get('coupon')
        if coupon:
            # Update coupon usage count and save
            coupon.uses += 1
            coupon.save()
        
        order = Order.objects.create(**validated_data)
        return order
