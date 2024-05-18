from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            id=validated_data['id'],
            password=validated_data['password'],
            phone_number=validated_data['phone_number']
        )
        return user

    class Meta:
        model = User
        fields = '__all__'
