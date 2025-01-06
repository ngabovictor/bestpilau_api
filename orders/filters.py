
from django_filters import rest_framework as filters, UUIDFilter, BaseInFilter, CharFilter
from .models import Order

class CharInFilter(BaseInFilter, CharFilter):
    pass


class OrderFilter(filters.FilterSet):
    status__in = CharInFilter(field_name='status', lookup_expr='in',)
    created_at__gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', input_formats=['%Y-%m-%dT%H:%M:%S.%f'])
    created_at__lte = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', input_formats=['%Y-%m-%dT%H:%M:%S.%f'])
    outlet = UUIDFilter(field_name='outlet')
    customer = UUIDFilter(field_name='customer')
    assigned_rider = UUIDFilter(field_name='assigned_rider')
    created_by = UUIDFilter(field_name='created_by')

    class Meta:
        model = Order
        fields = [
            'status__in', 
            'created_at__gte', 
            'created_at__lte', 
            'reference_code', 
            'outlet', 
            'customer', 
            'assigned_rider', 
            'created_by'
        ]