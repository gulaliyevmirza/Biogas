"""
Model unit testləri
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from apps.sensors.models import Sensor, SensorData
from apps.feedstock.models import Feedstock, Digestate
from apps.alerts.models import Alert
from apps.analytics.models import ProductionLog, AIPrediction
from apps.economic.models import EconomicData
from apps.process.models import ProcessOptimization
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='modeltest', password='Pass123!',
        email='mt@test.com', role='muhendis'
    )


@pytest.fixture
def sensor(db):
    return Sensor.objects.create(
        name='Test Sensor', type='temperature', unit='°C',
        location='Zone A', threshold_min=30.0, threshold_max=55.0
    )


class TestUserModel:
    def test_user_creation(self, db):
        u = User.objects.create_user(
            username='u1', password='p', email='u1@test.com', role='admin'
        )
        assert u.is_admin_user is True
        assert u.is_engineer is False
        assert str(u) == 'u1 (Admin)'

    def test_engineer_role(self, db):
        u = User.objects.create_user(
            username='eng', password='p', email='e@test.com', role='muhendis'
        )
        assert u.is_engineer is True
        assert u.is_admin_user is False


class TestFeedstockModel:
    def test_create_feedstock(self, db):
        f = Feedstock.objects.create(
            type='grape', quantity=500.0, status='pending'
        )
        assert f.status == 'pending'
        assert str(f) == f'Üzüm tullantısı - 500.0 kq ({f.received_date})'

    def test_status_choices(self, db):
        for s in ['pending', 'processing', 'completed', 'rejected']:
            f = Feedstock.objects.create(type='apple', quantity=100, status=s)
            assert f.status == s


class TestDigestateModel:
    def test_total_value(self, db):
        d = Digestate.objects.create(
            quantity=10.0, quality_grade='A', price_per_ton=Decimal('150.00')
        )
        assert d.total_value == 1500.0

    def test_sold_flag(self, db):
        d = Digestate.objects.create(
            quantity=5.0, quality_grade='B', price_per_ton=Decimal('100.00')
        )
        assert d.sold is False
        d.sold = True
        d.save()
        d.refresh_from_db()
        assert d.sold is True


class TestAlertModel:
    def test_alert_creation(self, sensor, db):
        a = Alert.objects.create(
            sensor=sensor, message='Test xəbərdarlıq', severity='warning'
        )
        assert a.is_read is False
        assert a.severity == 'warning'

    def test_mark_read(self, db):
        a = Alert.objects.create(message='Test', severity='info')
        assert a.is_read is False
        a.mark_read()
        assert a.is_read is True
        assert a.read_at is not None


class TestEconomicModel:
    def test_auto_calculate_on_save(self, db):
        e = EconomicData.objects.create(
            date=timezone.now().date(),
            revenue_gas=Decimal('500.00'),
            revenue_fertilizer=Decimal('200.00'),
            revenue_other=Decimal('50.00'),
            expenses=Decimal('300.00'),
        )
        assert e.total_revenue == Decimal('750.00')
        assert e.net_profit == Decimal('450.00')
        assert e.roi_percentage == pytest.approx(150.0, rel=0.01)

    def test_roi_zero_expenses(self, db):
        e = EconomicData.objects.create(
            date=timezone.now().date(),
            revenue_gas=Decimal('100.00'),
            expenses=Decimal('0.00'),
        )
        assert e.roi_percentage == 0.0


class TestProductionLog:
    def test_create_log(self, db):
        log = ProductionLog.objects.create(
            date=timezone.now().date(),
            methane_output=150.5,
            biogas_output=200.0,
            energy_generated=300.0,
            co2_reduction=120.0,
            temperature_avg=37.5,
            ph_avg=7.2,
        )
        assert 'İstehsal' in str(log)
        assert log.methane_output == 150.5


class TestProcessOptimization:
    def test_apply_optimization(self, user, db):
        opt = ProcessOptimization.objects.create(
            parameter_name='Temperatur',
            current_value=35.0,
            recommended_value=38.0,
            unit='°C',
            reason='Metanogenlər üçün optimal temperatur',
        )
        assert opt.applied is False
        opt.apply(user=user)
        assert opt.applied is True
        assert opt.applied_by == user
        assert opt.applied_at is not None

    def test_str_representation(self, db):
        opt = ProcessOptimization.objects.create(
            parameter_name='pH', current_value=6.5,
            recommended_value=7.2, reason='Optimal pH'
        )
        assert 'pH' in str(opt)
        assert '→' in str(opt)
