from rest_framework import serializers
from utils.serializers import ModelSerializer
from .models import Pub


class PubSerializer(ModelSerializer):
    class Meta:
        model = Pub
        fields = [
            'id',
            'title',
            'content', 
            'image',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
