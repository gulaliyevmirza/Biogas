from rest_framework import serializers
from .models import ProcessOptimization


class ProcessOptimizationSerializer(serializers.ModelSerializer):
    applied_by_name = serializers.CharField(
        source='applied_by.get_full_name', read_only=True
    )

    class Meta:
        model = ProcessOptimization
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'applied', 'applied_at', 'applied_by')
