from rest_framework.serializers import ModelSerializer
from authentication.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'is_rider', 'is_active', 'is_staff', 'outlets', 'rider_id')

    def to_representation(self, instance):
        serialized_data = super(UserSerializer, self).to_representation(instance)
        serialized_data['outlets'] = instance.outlets.all().values('id', 'name')
        serialized_data['can_use_dashboard'] = instance.is_staff or instance.outlets.exists()
        return serialized_data
    
    
    def create(self, validated_data):
        outlets = validated_data.pop('outlets', [])
        user = super().create(validated_data)
        if outlets:
            user.outlets.set(outlets)
        return user

    def update(self, instance, validated_data):
        outlets = validated_data.pop('outlets', None)
        user = super().update(instance, validated_data)
        if outlets is not None:
            user.outlets.set(outlets)
        return user
