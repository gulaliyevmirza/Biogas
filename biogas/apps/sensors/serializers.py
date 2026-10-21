from rest_framework import serializers
from .models import Sensor, SensorData


class SensorSerializer(serializers.ModelSerializer):
    latest_value = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Sensor
        fields = '__all__'

    def get_latest_value(self, obj):
        latest = obj.data_points.first()
        return latest.value if latest else None

    def get_status(self, obj):
        latest = obj.data_points.first()
        if not latest:
            return 'no_data'
        return obj.check_threshold(latest.value)


class SensorDataSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    unit = serializers.CharField(source='sensor.unit', read_only=True)

    class Meta:
        model = SensorData
        fields = ('id', 'sensor', 'sensor_name', 'value', 'unit', 'timestamp', 'is_anomaly')
        read_only_fields = ('id', 'is_anomaly')


class SensorDataBulkSerializer(serializers.Serializer):
    """For IoT bulk data ingestion"""
    sensor_id = serializers.IntegerField()
    value = serializers.FloatField()
    timestamp = serializers.DateTimeField(required=False)

    def validate_sensor_id(self, value):
        try:
            Sensor.objects.get(pk=value, is_active=True)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError('Aktiv sensor tapılmadı.')
        return value


class BulkDataIngestionSerializer(serializers.Serializer):
    data = SensorDataBulkSerializer(many=True)

    def create(self, validated_data):
        data_points = validated_data['data']
        created = []
        for item in data_points:
            sensor = Sensor.objects.get(pk=item['sensor_id'])
            kwargs = {'sensor': sensor, 'value': item['value']}
            if 'timestamp' in item:
                kwargs['timestamp'] = item['timestamp']
            obj = SensorData(**kwargs)
            obj.save()
            created.append(obj)
        return created
