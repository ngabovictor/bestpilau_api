from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.none()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Order.objects.all()
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated:
            # Get orders where user is the customer
            customer_orders = queryset.filter(customer=user)
            # Get orders from outlets where user works
            worker_orders = queryset.filter(outlet__workers=user)
            
            return (customer_orders | worker_orders).distinct()

        return queryset.none()
