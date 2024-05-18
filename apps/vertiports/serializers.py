from .models import Vertiport
from rest_framework import serializers


class VertiportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vertiport
        fields = '__all__'
