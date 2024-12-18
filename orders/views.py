from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from utils.filters import DynamicModelFilter

from .models import Order
from .serializers import OrderSerializer
from payments import utils as PaymentUtil


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.none()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['outlet', 'customer', 'status', 'assigned_rider', 'created_by', 'created_at',]
    filter_class = DynamicModelFilter
    search_fields = ['customer__email', 'customer__first_name', 'customer__last_name', 'order_number']
    ordering_fields = ['created_at', 'total_amount', 'status', 'payment_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Order.objects.all()
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated:
            # Get orders where user is the customer
            customer_orders = queryset.filter(customer=user) | queryset.filter(created_by=user)
            # Get orders from outlets where user works
            worker_orders = queryset.filter(outlet__workers=user)
            
            return (customer_orders | worker_orders).distinct()

        return queryset.none()
    
    
    def create(self, request, *args, **kwargs):
        payment_account = request.data.get('payment_account')
        response = super().create(request, *args, **kwargs)
        order = Order.objects.get(id=response.data['id'])
        PaymentUtil.initialize_payment(order, payment_account)
        # Refresh order from database to get latest changes
        order.refresh_from_db()
        response.data = OrderSerializer(order).data
        return response
    
    
