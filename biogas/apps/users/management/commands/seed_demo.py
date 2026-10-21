"""
Demo data seed əmri: python manage.py seed_demo
"""
import random
from datetime import timedelta, date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Demo data yükləyir (inkişaf üçün)'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Demo data yüklənir...')

        # ── Users ──────────────────────────────────────────────────────────
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@biogas.az', 'first_name': 'Admin',
                'last_name': 'İstifadəçi', 'role': 'admin',
                'company': 'BioGas MMC', 'is_staff': True, 'is_superuser': True,
            }
        )
        admin.set_password('admin123')
        admin.save()

        eng, _ = User.objects.get_or_create(
            username='engineer',
            defaults={
                'email': 'eng@biogas.az', 'first_name': 'Əli',
                'last_name': 'Əliyev', 'role': 'muhendis', 'company': 'BioGas MMC',
            }
        )
        eng.set_password('eng123')
        eng.save()
        self.stdout.write('  ✓ İstifadəçilər yaradıldı')

        # ── Sensors ────────────────────────────────────────────────────────
        from apps.sensors.models import Sensor, SensorData
        sensors_config = [
            ('CH4 Sensoru #1', 'CH4', '%', 'Fermentator 1', 40, 70),
            ('CH4 Sensoru #2', 'CH4', '%', 'Fermentator 2', 40, 70),
            ('Temperatur #1', 'temperature', '°C', 'Fermentator 1', 33, 42),
            ('Temperatur #2', 'temperature', '°C', 'Fermentator 2', 33, 42),
            ('pH Sensoru', 'pH', 'pH', 'Fermentator 1', 6.5, 8.0),
            ('CO2 Sensoru', 'CO2', '%', 'Qaz kollektoru', 25, 45),
            ('H2S Sensoru', 'H2S', 'ppm', 'Çıxış xətti', 0, 500),
            ('ORP Sensoru', 'ORP', 'mV', 'Fermentator 1', -300, -100),
        ]
        sensors = []
        for name, stype, unit, loc, tmin, tmax in sensors_config:
            s, _ = Sensor.objects.get_or_create(
                name=name,
                defaults={
                    'type': stype, 'unit': unit, 'location': loc,
                    'threshold_min': tmin, 'threshold_max': tmax, 'is_active': True,
                }
            )
            sensors.append(s)

        # Generate 7 days of sensor data
        now = timezone.now()
        base_values = {
            'CH4': 58.0, 'temperature': 37.5, 'pH': 7.2,
            'CO2': 35.0, 'H2S': 150.0, 'ORP': -200.0,
        }
        data_to_create = []
        for s in sensors:
            base = base_values.get(s.type, 50.0)
            for hours_ago in range(7 * 24, 0, -1):
                noise = random.gauss(0, base * 0.03)
                val = max(0, base + noise)
                data_to_create.append(SensorData(
                    sensor=s, value=round(val, 3),
                    timestamp=now - timedelta(hours=hours_ago),
                    is_anomaly=False,
                ))
        SensorData.objects.bulk_create(data_to_create, ignore_conflicts=True)
        self.stdout.write(f'  ✓ {len(sensors)} sensor, {len(data_to_create)} data nöqtəsi')

        # ── Feedstock ──────────────────────────────────────────────────────
        from apps.feedstock.models import Feedstock, Digestate
        feed_types = ['grape', 'pomegranate', 'apple', 'pear', 'plum']
        for i in range(15):
            Feedstock.objects.get_or_create(
                received_date=date.today() - timedelta(days=i * 2),
                type=feed_types[i % len(feed_types)],
                defaults={
                    'quantity': random.uniform(200, 800),
                    'status': random.choice(['pending', 'processing', 'completed']),
                    'supplier': f'Tədarükçü #{i + 1}',
                }
            )

        for i in range(10):
            Digestate.objects.get_or_create(
                production_date=date.today() - timedelta(days=i * 3),
                defaults={
                    'quantity': round(random.uniform(1, 8), 2),
                    'quality_grade': random.choice(['A', 'B', 'C']),
                    'price_per_ton': Decimal(str(round(random.uniform(80, 200), 2))),
                    'sold': i % 3 == 0,
                }
            )
        self.stdout.write('  ✓ Xammal & digestat məlumatları yaradıldı')

        # ── Production Logs ────────────────────────────────────────────────
        from apps.analytics.models import ProductionLog
        for days_ago in range(30):
            d = date.today() - timedelta(days=days_ago)
            ProductionLog.objects.get_or_create(
                date=d,
                defaults={
                    'methane_output': round(random.uniform(120, 200), 2),
                    'biogas_output': round(random.uniform(180, 280), 2),
                    'energy_generated': round(random.uniform(250, 400), 2),
                    'co2_reduction': round(random.uniform(80, 150), 2),
                    'temperature_avg': round(random.uniform(35, 40), 2),
                    'ph_avg': round(random.uniform(6.8, 7.6), 2),
                    'feedstock_used': round(random.uniform(300, 600), 2),
                }
            )
        self.stdout.write('  ✓ 30 günlük istehsal jurnalı yaradıldı')

        # ── Economic Data ──────────────────────────────────────────────────
        from apps.economic.models import EconomicData
        for days_ago in range(30):
            d = date.today() - timedelta(days=days_ago)
            EconomicData.objects.get_or_create(
                date=d,
                defaults={
                    'revenue_gas': Decimal(str(round(random.uniform(150, 350), 2))),
                    'revenue_fertilizer': Decimal(str(round(random.uniform(50, 180), 2))),
                    'revenue_other': Decimal(str(round(random.uniform(0, 50), 2))),
                    'expenses': Decimal(str(round(random.uniform(100, 200), 2))),
                }
            )
        self.stdout.write('  ✓ 30 günlük iqtisadi data yaradıldı')

        # ── Process Optimizations ──────────────────────────────────────────
        from apps.process.models import ProcessOptimization
        opts = [
            ('Temperatur', 35.5, 38.0, '°C', 'Metanogenesis üçün optimal temperatur 35-40°C arasındadır.', 'high'),
            ('pH Səviyyəsi', 6.8, 7.2, 'pH', 'Bakteriyaların aktivliyi üçün neytral pH tövsiyə olunur.', 'medium'),
            ('Qarışdırma Sürəti', 20, 30, 'RPM', 'Daha yaxşı kütlə köçürməsi üçün artırılmış sürət lazımdır.', 'low'),
            ('Xammal Yükləmə Tezliyi', 2, 3, 'dəfə/gün', 'Qida mənbəyinin daha tez-tez verilməsi sabitliyi artırır.', 'medium'),
        ]
        for pname, cur, rec, unit, reason, priority in opts:
            ProcessOptimization.objects.get_or_create(
                parameter_name=pname,
                applied=False,
                defaults={
                    'current_value': cur, 'recommended_value': rec,
                    'unit': unit, 'reason': reason, 'priority': priority,
                }
            )
        self.stdout.write('  ✓ Proses optimallaşdırma tövsiyələri yaradıldı')

        self.stdout.write(self.style.SUCCESS('\n🎉 Demo data uğurla yükləndi!'))
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Mühendis: engineer / eng123')
        self.stdout.write('   Admin panel: http://localhost:8000/admin/')
