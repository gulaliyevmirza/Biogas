"""
Sensor API testləri
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.sensors.models import Sensor, SensorData

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(
        username='sensortest', password='Pass123!', email='st@test.com'
    )
    client = APIClient()
    resp = client.post(reverse('login'), {'username': 'sensortest', 'password': 'Pass123!'})
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {resp.data["access"]}')
    return client


@pytest.fixture
def sample_sensor(db):
    return Sensor.objects.create(
        name='Test CH4 Sensoru',
        type='CH4',
        unit='%',
        location='Fermentator 1',
        threshold_min=40.0,
        threshold_max=70.0,
        is_active=True,
    )


class TestSensorCRUD:
    def test_create_sensor(self, auth_client, db):
        url = reverse('sensor-list')
        data = {
            'name': 'pH Sensoru',
            'type': 'pH',
            'unit': 'pH',
            'location': 'Fermentator 2',
            'threshold_min': 6.5,
            'threshold_max': 8.0,
            'is_active': True,
        }
        resp = auth_client.post(url, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['name'] == 'pH Sensoru'
        assert Sensor.objects.filter(name='pH Sensoru').exists()

    def test_list_sensors(self, auth_client, sample_sensor, db):
        url = reverse('sensor-list')
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_filter_by_type(self, auth_client, sample_sensor, db):
        url = reverse('sensor-list') + '?type=CH4'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        for s in resp.data['results']:
            assert s['type'] == 'CH4'

    def test_get_sensor_data(self, auth_client, sample_sensor, db):
        SensorData.objects.create(sensor=sample_sensor, value=55.0)
        SensorData.objects.create(sensor=sample_sensor, value=58.0)
        url = reverse('sensor-sensor-data', kwargs={'pk': sample_sensor.pk})
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] == 2

    def test_unauthenticated_access_blocked(self, api_client, db):
        url = reverse('sensor-list')
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestSensorThresholds:
    def test_threshold_normal(self, sample_sensor, db):
        assert sample_sensor.check_threshold(55.0) == 'normal'

    def test_threshold_warning_below(self, sample_sensor, db):
        # Just below min (40) but not >20% deviation
        assert sample_sensor.check_threshold(39.0) == 'warning'

    def test_threshold_critical_above(self, sample_sensor, db):
        # >20% above max (70)
        assert sample_sensor.check_threshold(85.0) == 'critical'

    def test_anomaly_flag_on_save(self, sample_sensor, db):
        data = SensorData(sensor=sample_sensor, value=90.0)  # Critical
        data.save()
        assert data.is_anomaly is True

    def test_normal_data_not_anomaly(self, sample_sensor, db):
        data = SensorData(sensor=sample_sensor, value=55.0)
        data.save()
        assert data.is_anomaly is False


class TestBulkIngestion:
    def test_bulk_ingest(self, auth_client, sample_sensor, db):
        url = reverse('sensor-bulk-ingest')
        payload = {
            'data': [
                {'sensor_id': sample_sensor.id, 'value': 52.1},
                {'sensor_id': sample_sensor.id, 'value': 53.4},
                {'sensor_id': sample_sensor.id, 'value': 54.0},
            ]
        }
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['created'] == 3

    def test_bulk_ingest_invalid_sensor(self, auth_client, db):
        url = reverse('sensor-bulk-ingest')
        payload = {'data': [{'sensor_id': 99999, 'value': 50.0}]}
        resp = auth_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
