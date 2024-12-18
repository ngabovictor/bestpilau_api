from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Coupon
from .serializers import CouponSerializer



class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.filter(state=True)
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    
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
    
    
        

    @action(detail=False, methods=['get'], url_path='validate', url_name='validate')
    def validate_coupon(self, request):
        code = request.query_params.get('code')
        outlet_id = request.query_params.get('outlet_id')
        
        if not code:
            return Response(
                {'detail': 'Coupon code is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not outlet_id:
            return Response(
                {'detail': 'Outlet ID is required'},
                status=status.HTTP_400_BAD_REQUEST 
            )

        try:
            coupon = Coupon.objects.get(
                code=code,
                state=True,
                effective_at__lte=timezone.now(),
                expires_at__gte=timezone.now()  # Changed from gte to lte
            )
            
            # Check if coupon is valid for the user
            user = request.user
            if not coupon.all_users_allowed and not coupon.allowed_users.filter(id=user.id).exists():
                raise Coupon.DoesNotExist()

            # Check if coupon is valid for the outlet
            if not coupon.all_outlets_allowed and not coupon.allowed_outlets.filter(id=outlet_id).exists():
                raise Coupon.DoesNotExist()
            
            # Check if coupon has exceeded max uses
            if coupon.max_uses and coupon.uses >= coupon.max_uses:
                raise Coupon.DoesNotExist()

            serializer = self.get_serializer(coupon)
            return Response(serializer.data)

        except Coupon.DoesNotExist:
            return Response(
                {'detail': 'Invalid coupon code'},
                status=status.HTTP_404_NOT_FOUND
            )
    
