from .models import State, Optimization
from rest_framework import serializers


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        exclude = ['user', 'vertiport']


class OptimizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Optimization
        exclude = ['state']
