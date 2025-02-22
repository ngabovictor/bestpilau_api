from rest_framework import serializers
from authentication.serializers.user_serializer import UserMiniSerializer
from utils.serializers import ModelSerializer
from .models import Outlet, WORKING_HOURS_DEFINITION_SCHEMA, LOCATION_DEFINITION_SCHEMA
from jsonschema import validate as jsonschema_validate, ValidationError as JSONSchemaValidationError


class OutletSerializer(ModelSerializer):
    class Meta:
        model = Outlet
        fields = [
            'id',
            'name', 
            'image',
            'phone_number',
            'email',
            'is_open',
            'working_hours',
            'address',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def to_representation(self, instance):
        serialized_data = super(OutletSerializer, self).to_representation(instance)
        serialized_data['workers'] = UserMiniSerializer(instance.workers.all(), many=True).data
        return serialized_data
        
    def validate_working_hours(self, value):
        try:
            jsonschema_validate(instance=value, schema=WORKING_HOURS_DEFINITION_SCHEMA)
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid working hours data: {e.message}")
        return value

    def validate_address(self, value):
        try:
            jsonschema_validate(instance=value, schema=LOCATION_DEFINITION_SCHEMA) 
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid address data: {e.message}")
        return value
        
        
