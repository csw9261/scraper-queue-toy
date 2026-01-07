# Web Scraper Toy Project

Django + Celery + Redis 기반의 비동기 웹 스크래퍼 토이 프로젝트입니다.

## 개발 환경 시작 가이드

### 1. 인프라 실행 (Docker)
DB(PostgreSQL)와 Message Broker(Redis)를 실행합니다.
```powershell
# 컨테이너 실행
docker compose -f docker-compose.dev.yml up -d

# 컨테이너 중지
docker compose -f docker-compose.dev.yml down
```

### 2. 백엔드 설정 (Django)
backend 디렉토리에서 작업을 수행합니다.

```powershell
cd backend

# 가상환경 활성화 (최초 1회)
python -m venv venv
.\venv\Scripts\Activate

# 패키지 설치
pip install -r requirements.txt

# DB 마이그레이션
python manage.py makemigrations
python manage.py migrate

# Django 서버 실행
python manage.py runserver
```

### 3. Celery 실행
비동기 작업을 위해 별도의 터미널에서 실행해야 합니다. (가상환경 활성화 필요)

```powershell
# Worker 실행 (스크래핑 작업 수행)
# Windows에서는 --pool=solo 옵션이 필요할 수 있습니다.
celery -A config worker -l info --pool=solo

# Beat 실행 (스케줄링 작업 관리)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 기술 스택
- Backend: Django, DRF, Celery
- Database: PostgreSQL
- Broker: Redis
- Frontend: Node.js (Express)

## 프로젝트 구조
- backend/: Django 프로젝트 및 스크래핑 로직
- frontend/: Node.js 기반 프런트엔드 (준비 중)
- docker-compose.yml: 전체 서비스 운영용
- docker-compose.dev.yml: 로컬 개발용 인프라 (DB, Redis)
