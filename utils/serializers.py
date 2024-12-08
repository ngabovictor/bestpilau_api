from rest_framework import serializers


class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def create(self, validated_data):
        validated_data["created_by"] = self.get_current_user()
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        return super().update(instance=instance, validated_data=validated_data)

    def get_current_user(self):
        try:
            return self.context.get('request').user
        except:
            return None
