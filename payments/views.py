from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from payments import utils as PaymentUtil


class TransactionViewSet(ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['reference_code', 'order__reference_code']
    filterset_fields = ['status', 'payment_method', 'transaction_type', 'refund_status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Transaction.objects.all()
        user = self.request.user

        if user.is_staff:
            return queryset

        if user.is_authenticated and user.outlet_set.exists():
            # Get transactions from outlets where user works
            return queryset.filter(order__outlet__workers=user)

        # Customers can only see their own transactions
        return queryset.filter(order__customer=user)



class FdiCallbackView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        PaymentUtil.handle_fdi_callback(request.data)
        return Response({'message': 'Callback received'}, status=200)
