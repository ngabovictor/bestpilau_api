from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Outlet
from jsonschema import validate as jsonschema_validate, ValidationError as JSONSchemaValidationError


class OutletSerializer(ModelSerializer):
    class Meta:
        model = Outlet
        fields = [
            'id',
            'name', 
            'phone_number',
            'email',
            'is_open',
            'working_hours',
            'address',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def validate_working_hours(self, value):
        try:
            jsonschema_validate(instance=value, schema=Outlet.WORKING_HOURS_SCHEMA)
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid working hours data: {e.message}")
        return value

    def validate_address(self, value):
        try:
            jsonschema_validate(instance=value, schema=Outlet.ADDRESS_SCHEMA) 
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid address data: {e.message}")
        return value
        
        
