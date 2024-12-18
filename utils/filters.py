import django_filters
from django.db import models

class DynamicModelFilter(django_filters.FilterSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.model = kwargs['queryset'].model
        
        # Get all model fields
        model_fields = self.Meta.model._meta.fields 

        # Exclude ImageField, FileField, and JSONField
        self.Meta.fields = [
            field.name for field in model_fields 
            if not isinstance(field, (models.ImageField, models.FileField, models.JSONField))
        ]

        # Dynamically create filters for the remaining fields
        for field_name in self.Meta.fields:
            field = self.Meta.model._meta.get_field(field_name)
            if isinstance(field, models.CharField):
                self.filters[field_name] = django_filters.CharFilter(lookup_expr='icontains')
            elif isinstance(field, models.DateTimeField):
                self.filters[field_name] = django_filters.DateTimeFilter()
                self.filters[f'{field_name}__lt'] = django_filters.DateTimeFilter(field_name=field_name, lookup_expr='lt')
                self.filters[f'{field_name}__gt'] = django_filters.DateTimeFilter(field_name=field_name, lookup_expr='gt')
                self.filters[f'{field_name}__gte'] = django_filters.DateTimeFilter(field_name=field_name, lookup_expr='gte')
                self.filters[f'{field_name}__lte'] = django_filters.DateTimeFilter(field_name=field_name, lookup_expr='lte')
            elif isinstance(field, models.TimeField):
                self.filters[field_name] = django_filters.TimeFilter()
            elif isinstance(field, models.DateField):
                self.filters[field_name] = django_filters.DateFilter()

    class Meta:
        pass  # No need to specify fields here