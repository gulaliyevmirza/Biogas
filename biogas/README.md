# 🌿 BioExtract & BIOGAS 4.0 — Smart Biometan Platforması

Django 4.2 + DRF + PostgreSQL + Celery + Docker ilə qurulmuş cloud-ready backend.

---

## 🗂️ Layihə Strukturu

```
biogas/
├── config/                  # Django konfiqurasiyası
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── apps/
│   ├── users/               # Xüsusi istifadəçi modeli, JWT auth
│   ├── sensors/             # Sensor & SensorData, IoT ingest
│   ├── analytics/           # İstehsal jurnalları, AI proqnoz
│   ├── economic/            # İqtisadi göstəricilər, ROI
│   ├── feedstock/           # Xammal & Digestat
│   ├── alerts/              # Xəbərdarlıqlar, email
│   └── process/             # Proses optimallaşdırması
├── tests/                   # pytest testləri
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
└── .env.example
```

---

## ⚡ Sürətli Başlanğıc (Docker ilə)

### 1. Layihəni klon et
```bash
git clone <repo-url>
cd biogas
```

### 2. Environment faylını hazırla
```bash
cp .env.example .env
# .env faylını redaktə et: SECRET_KEY, DB şifrəsi, email məlumatları
```

### 3. Docker ilə qur və işə sal
```bash
docker compose up --build -d
```

### 4. İlk admin istifadəçisini yarat
```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Hazırdır! 🎉
- API: http://localhost:8000/api/
- Admin panel: http://localhost:8000/admin/

---

## 🔧 Yerli İnkişaf (Docker olmadan)

```bash
# Virtual mühit
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# Asılılıqları quraşdır
pip install -r requirements.txt

# .env faylı
cp .env.example .env
# .env-i redaktə et, DB_HOST=localhost, DEBUG=1

# PostgreSQL verilənlər bazası yarat
createdb biogas_db

# Migrasiyalar
python manage.py migrate

# Admin istifadəçisi
python manage.py createsuperuser

# Serveri işə sal
python manage.py runserver

# Ayrı terminalda Celery worker
celery -A config worker --loglevel=info

# Ayrı terminalda Celery beat
celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## 🔌 API Sənədləri

### Autentifikasiya

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| POST | `/api/auth/register/` | Qeydiyyat |
| POST | `/api/auth/login/` | JWT token al |
| POST | `/api/auth/refresh/` | Tokeni yenilə |
| GET | `/api/auth/profile/` | Profil məlumatları |
| PUT | `/api/auth/profile/` | Profili yenilə |
| POST | `/api/auth/logout/` | Çıxış (token blacklist) |

### Sensorlar

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/api/sensors/` | Bütün sensorlar |
| POST | `/api/sensors/` | Sensor yarat |
| GET | `/api/sensors/{id}/data/` | Sensor dataları |
| GET | `/api/sensors/live/` | Canlı sensor dəyərləri |
| POST | `/api/sensors/data/bulk/` | IoT bulk data |

### Analitika

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/api/analytics/live/` | Canlı panel |
| GET | `/api/analytics/history/?start=&end=` | Tarixçə |
| GET | `/api/analytics/methane-prediction/` | AI proqnozu |
| GET | `/api/analytics/daily-report/?date=` | Günlük hesabat |
| GET | `/api/analytics/monthly-report/?month=` | Aylıq hesabat |

### İqtisadi

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/api/economic/summary/?period=` | Xülasə (day/week/month/year) |
| GET | `/api/economic/revenue-breakdown/` | Gəlir bölgüsü |
| GET | `/api/economic/roi-calculator/` | ROI kalkulyatoru |

### Xammal & Digestat

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET/POST | `/api/feedstock/feedstock/` | Xammal siyahısı/yarat |
| PUT | `/api/feedstock/feedstock/{id}/status/` | Status yenilə |
| GET/POST | `/api/feedstock/digestate/` | Digestat siyahısı/yarat |
| POST | `/api/feedstock/digestate/{id}/sell/` | Digestat sat |

### Xəbərdarlıqlar

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/api/alerts/` | Oxunmamış alertlər |
| POST | `/api/alerts/{id}/read/` | Oxunmuş kimi işarələ |
| POST | `/api/alerts/read-all/` | Hamısını oxunmuş et |
| GET | `/api/alerts/history/` | Alert tarixçəsi |

### Proses

| Method | Endpoint | Təsvir |
|--------|----------|--------|
| GET | `/api/process/optimization/latest/` | Tətbiq edilməmiş optimallaşdırmalar |
| POST | `/api/process/optimization/{id}/apply/` | Optimallaşdırmanı tətbiq et |
| GET | `/api/process/optimization/logs/` | Tətbiq edilmiş qeydlər |

---

## 🔑 JWT İstifadəsi

```bash
# Token al
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Cavab:
# {"access": "eyJ...", "refresh": "eyJ..."}

# API çağırışı
curl http://localhost:8000/api/sensors/ \
  -H "Authorization: Bearer eyJ..."
```

---

## 🤖 Celery Tasklar

| Task | Cədvəl | Təsvir |
|------|--------|--------|
| `predict_methane` | Hər 6 saatda | AI metan proqnozu |
| `generate_daily_summary` | Hər gün 23:00 | İqtisadi hesabat |
| `check_all_sensor_thresholds` | Hər saat | Sensor anomaliya yoxlaması |

Manual işə salmaq üçün:
```bash
# Docker ilə
docker compose exec celery_worker celery -A config call apps.analytics.tasks.predict_methane

# Yerli
celery -A config call apps.analytics.tasks.predict_methane
```

---

## 🧪 Testlər

```bash
# Bütün testlər
pytest

# Coverage ilə
pytest --cov=apps --cov-report=html

# Konkret test faylı
pytest tests/test_auth.py -v

# Konkret test
pytest tests/test_sensors.py::TestSensorThresholds::test_threshold_critical_above -v
```

---

## ☁️ Cloud Deploy (AWS EC2 nümunəsi)

```bash
# 1. EC2-yə qoşul
ssh -i key.pem ubuntu@<ec2-ip>

# 2. Docker quraşdır
sudo apt update && sudo apt install docker.io docker-compose-plugin -y

# 3. Layihəni klon et
git clone <repo-url> && cd biogas

# 4. Production .env hazırla
nano .env   # DEBUG=0, real SECRET_KEY, DB məlumatları

# 5. İşə sal
docker compose up -d --build

# 6. SSL üçün Nginx + Certbot əlavə et
sudo apt install certbot python3-certbot-nginx -y
```

---

## 🛠️ Faydalı Əmrlər

```bash
# Migrasiya yarat
docker compose exec web python manage.py makemigrations

# Migrasiya tətbiq et
docker compose exec web python manage.py migrate

# Django shell
docker compose exec web python manage.py shell

# Log izlə
docker compose logs -f web
docker compose logs -f celery_worker

# Servisi yeniden başlat
docker compose restart web
```

---

## 📊 Məlumat Bazası Sxemi

```
User ──────────────── ProcessOptimization
                             │
Sensor ─────────────── SensorData
  │                          │
  └──────────────────── Alert
                          
Feedstock          Digestate
                          
ProductionLog      AIPrediction      EconomicData
```

---

## 🔒 Təhlükəsizlik

- JWT token blacklist (çıxışda etibarsız olur)
- Rate limiting: Anonim 100/saat, İstifadəçi 1000/saat
- CORS konfiqurasiyası
- Production-da HTTPS məcburidir (`SECURE_HSTS_SECONDS`)
- Bütün konfiqurasiya environment variables vasitəsilə

---

## 📧 Əlaqə

**BioExtract & BIOGAS 4.0** — Azərbaycan üzüm və meyvə tullantılarından bioaktiv maddələr və biogaz istehsalının rəqəmsallaşdırılması platforması.
