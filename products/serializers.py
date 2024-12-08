from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Product, ProductCategory
from jsonschema import validate as jsonschema_validate, ValidationError as JSONSchemaValidationError


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'outlet',
            'name',
            'image',
            'caption',
            'parent',
            'vendor',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'outlet',
            'name',
            'caption',
            'image',
            'category',
            'description',
            'ingredients',
            'price',
            'is_available',
            'processing_time',
            'options',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_options(self, value):
        try:
            jsonschema_validate(instance=value, schema=Product.OPTIONS_SCHEMA)
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid options data: {e.message}")
        return value
    
    def validate_ingredients(self, value):
        try:
            jsonschema_validate(instance=value, schema=Product.INGREDIENTS_SCHEMA)
        except JSONSchemaValidationError as e:
            raise serializers.ValidationError(f"Invalid ingredients data: {e.message}")
        return value
