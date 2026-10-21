from rest_framework import serializers
from django.utils import timezone
from .models import Feedstock, Digestate


class FeedstockSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Feedstock
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class FeedstockStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedstock
        fields = ('status', 'notes')


class DigestateSerializer(serializers.ModelSerializer):
    quality_grade_display = serializers.CharField(
        source='get_quality_grade_display', read_only=True
    )
    total_value = serializers.FloatField(read_only=True)

    class Meta:
        model = Digestate
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class DigestateSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digestate
        fields = ('buyer', 'sold_date', 'price_per_ton')

    def validate(self, attrs):
        if not attrs.get('sold_date'):
            attrs['sold_date'] = timezone.now().date()
        return attrs
