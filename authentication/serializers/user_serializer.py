from rest_framework.serializers import ModelSerializer
from authentication.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'username', 'is_rider',)

    def to_representation(self, instance):
        serialized_data = super(UserSerializer, self).to_representation(instance)
        return serialized_data
