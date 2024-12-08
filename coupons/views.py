from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Coupon
from .serializers import CouponSerializer


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.none()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated:
            code = self.request.query_params.get('code')
            if code:
                return queryset.filter(code=code)

            # Get coupons for outlets user works at
            user_outlet_coupons = queryset.filter(allowed_outlets__workers=user)
            # Get coupons allowed for all outlets
            all_outlet_coupons = queryset.filter(all_outlets_allowed=True)
            
            return (user_outlet_coupons | all_outlet_coupons).distinct()

        # For unauthenticated users, only allow code lookup
        code = self.request.query_params.get('code')
        if code:
            return queryset.filter(code=code)
        return queryset.none()
    
