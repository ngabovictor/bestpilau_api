from utils.serializers import ModelSerializer
from rest_framework import serializers
from authentication.models import SavedAddress



class SavedAddressSerializer(ModelSerializer):

    address = serializers.JSONField()

    class Meta:
        model = SavedAddress
        fields = '__all__'

    def validate_address(self, value):
        address = SavedAddress(address=value)
        address.full_clean()
        return value