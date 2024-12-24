from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from payments.models import Transaction
from orders.models import Order
from authentication.models import User


class StatsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=False, url_path='stats', url_name='stats')
    def get_stats(self, request, *args, **kwargs):
        

        # Get today's date range
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        today_end = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.max.time()))

        # Get this week's date range
        week_start = today_start - timedelta(days=today.weekday())
        week_end = today_end

        # Get transactions stats
        today_transactions = Transaction.objects.filter(
            status='COMPLETED',
            created_at__range=(today_start, today_end)
        ).aggregate(total=Sum('amount'))

        week_transactions = Transaction.objects.filter(
            status='COMPLETED', 
            created_at__range=(week_start, week_end)
        ).aggregate(total=Sum('amount'))

        # Convert Decimal amounts to float for calculations
        today_amount = float(today_transactions['total'] or 0)
        week_amount = float(week_transactions['total'] or 0)

        # Get orders stats
        today_orders = Order.objects.filter(
            created_at__range=(today_start, today_end)
        ).exclude(status='CANCELLED')

        processing_orders = today_orders.filter(status__in=['CONFIRMED', 'PROCESSING']).count()
        completed_orders = today_orders.filter(status='COMPLETED').count()
        delivering_orders = today_orders.filter(status='DELIVERING').count()

        # Get riders stats
        riders = User.objects.filter(is_rider=True)
        active_riders = riders.filter(is_active=True)
        riders_on_delivery = User.objects.filter(
            is_rider=True,
            assigned_orders__status='DELIVERING'
        ).distinct().count()

        response_data = {
            'transactions': {
                'today': today_amount,
                'this_week': week_amount,
                'commissions': today_amount * 0.02  # 2% commission
            },
            'orders': {
                'today': today_orders.count(),
                'processing': processing_orders,
                'completed': completed_orders,
                'on_delivery': delivering_orders
            },
            'riders': {
                'total': riders.count(),
                'active': active_riders.count(),
                'on_delivery': riders_on_delivery
            }
        }
        return Response(response_data, status=200)