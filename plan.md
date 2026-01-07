# 웹 스크래퍼 토이 프로젝트 계획

## 프로젝트 개요
Django + Celery + Redis 기반 백엔드와 Node.js 기반 프론트엔드로 구성된 웹 스크래퍼

---

## 프로세스 흐름도

### 전체 아키텍처
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Docker Compose                                  │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌───────────┐ │
│  │  Frontend   │     │   Django    │     │    Redis    │     │  Celery   │ │
│  │  (Express)  │────▶│  (REST API) │────▶│   (Broker)  │────▶│  Worker   │ │
│  │  :3000      │     │  :8000      │     │  :6379      │     │           │ │
│  └─────────────┘     └─────────────┘     └─────────────┘     └───────────┘ │
│                             │                   │                   │       │
│                             ▼                   │                   ▼       │
│                      ┌───────────┐              │            ┌───────────┐  │
│                      │ PostgreSQL│              │            │ Scraping  │  │
│                      │   (DB)    │◀─────────────┼────────────│  Logic    │  │
│                      │   :5432   │              │            └───────────┘  │
│                      └───────────┘              │                           │
│                                                 │                           │
│                                          ┌──────┴──────┐                    │
│                                          │   Celery    │                    │
│                                          │    Beat     │                    │
│                                          │ (Scheduler) │                    │
│                                          └─────────────┘                    │
│                                                                             │
│  ┌─────────────┐                                                            │
│  │   Flower    │  (모니터링 대시보드)                                         │
│  │   :5555     │                                                            │
│  └─────────────┘                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 즉시 실행 흐름 (On-demand)
```
[사용자]                [Frontend]              [Django API]            [Redis]              [Celery Worker]
   │                       │                        │                      │                       │
   │  1. URL 입력          │                        │                      │                       │
   │──────────────────────▶│                        │                      │                       │
   │                       │  2. POST /api/scrape/  │                      │                       │
   │                       │───────────────────────▶│                      │                       │
   │                       │                        │  3. Task 생성        │                       │
   │                       │                        │  (status: pending)   │                       │
   │                       │                        │                      │                       │
   │                       │                        │  4. 태스크 큐 등록    │                       │
   │                       │                        │─────────────────────▶│                       │
   │                       │  5. 즉시 응답          │                      │                       │
   │                       │◀───────────────────────│                      │                       │
   │                       │  {id: 1, status: pending}                     │                       │
   │                       │                        │                      │  6. 태스크 수신       │
   │                       │                        │                      │─────────────────────▶│
   │                       │                        │                      │                       │
   │                       │                        │                      │  7. 스크래핑 실행     │
   │                       │                        │                      │  (status: running)    │
   │                       │                        │                      │                       │
   │                       │                        │                      │  8. 결과 저장         │
   │                       │                        │◀─────────────────────┼───────────────────────│
   │                       │                        │  (status: completed) │                       │
   │                       │                        │                      │                       │
   │  9. 결과 확인         │  10. GET /api/scrape/1 │                      │                       │
   │──────────────────────▶│───────────────────────▶│                      │                       │
   │                       │◀───────────────────────│                      │                       │
   │◀──────────────────────│  {result: {...}}       │                      │                       │
```

### 주기적 실행 흐름 (Scheduled - Celery Beat)
```
[Celery Beat]           [Redis]              [Celery Worker]           [DB]
      │                    │                       │                    │
      │  1. 스케줄 확인    │                       │                    │
      │  (매분 체크)       │                       │                    │
      │                    │                       │                    │
      │  2. 실행 시간 도달 │                       │                    │
      │  태스크 큐 등록    │                       │                    │
      │───────────────────▶│                       │                    │
      │                    │  3. 태스크 수신       │                    │
      │                    │──────────────────────▶│                    │
      │                    │                       │                    │
      │                    │                       │  4. 스크래핑 실행  │
      │                    │                       │───────────────────▶│
      │                    │                       │  결과 저장         │
      │                    │                       │                    │
      │                    │                       │  5. next_run 갱신  │
      │                    │                       │───────────────────▶│
      │                    │                       │                    │
```

### 재시도 흐름 (Retry Logic)
```
[Celery Worker]
      │
      │  스크래핑 시도
      │
      ▼
  ┌───────┐     성공     ┌───────────┐
  │ 요청  │─────────────▶│ completed │
  └───────┘              └───────────┘
      │
      │ 실패 (네트워크 오류 등)
      ▼
  ┌────────────┐
  │ 재시도 1/3 │──▶ 5초 대기 ──▶ 재시도
  └────────────┘
      │ 실패
      ▼
  ┌────────────┐
  │ 재시도 2/3 │──▶ 10초 대기 ──▶ 재시도
  └────────────┘
      │ 실패
      ▼
  ┌────────────┐
  │ 재시도 3/3 │──▶ 20초 대기 ──▶ 재시도
  └────────────┘
      │ 실패
      ▼
  ┌────────┐
  │ failed │ (error_message 저장)
  └────────┘
```

---

## 기술 스택
- **백엔드**: Django, Django REST Framework, Celery, Celery Beat, Redis, PostgreSQL
- **프론트엔드**: Node.js (Express), HTML, CSS, JavaScript
- **인프라**: Docker, Docker Compose

---

## 프로젝트 구조

```
scraper-queue-toy/
├── docker-compose.yml          # 프로덕션용
├── docker-compose.dev.yml      # 개발용 (DB, Redis만)
├── .vscode/
│   └── launch.json             # 디버깅 설정
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── celery.py
│   │   └── urls.py
│   └── scraper/
│       ├── __init__.py
│       ├── models.py
│       ├── tasks.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── server.js
    └── public/
        ├── index.html
        ├── css/
        │   └── style.css
        └── js/
            └── app.js
```

---

## 구현 단계

### 1. 인프라 구성 (Docker Compose)
- [ ] docker-compose.yml 작성
  - postgres 서비스 (DB)
  - redis 서비스 (Message Broker)
  - backend 서비스 (Django API)
  - celery-worker 서비스
  - celery-beat 서비스 (스케줄러)
  - flower 서비스 (모니터링)
  - frontend 서비스 (Node.js)
- [ ] Health Check 설정
  - postgres: pg_isready
  - redis: redis-cli ping
  - backend: curl health endpoint
  - depends_on + condition: service_healthy
- [ ] 로깅 설정
  - Django: console 로깅 (DEBUG 레벨)
  - Celery: task 시작/완료/실패 로그
  - 포맷: timestamp, level, module, message
- [ ] 네트워크 및 볼륨 설정

### 2. 백엔드 구성 (Django + Celery)
- [ ] Dockerfile 작성 (curl, netcat 설치 포함 - Health Check 및 DB 대기용)
- [ ] entrypoint.sh 작성 (DB 연결 대기 및 자동 마이그레이션 실행)
- [ ] requirements.txt (django, djangorestframework, celery, redis, requests, beautifulsoup4, django-cors-headers, django-celery-beat, psycopg2-binary)
- [ ] Django 프로젝트 설정
  - config/settings.py (CORS, Celery 설정)
  - config/celery.py (Celery 앱 설정)
  - config/urls.py (API 라우팅)

### 3. 스크래퍼 앱 구현
- [ ] models.py
  - ScrapeTask: url, status, result, error_message, created_at, updated_at
- [ ] tasks.py
  - Celery 스크래핑 태스크
  - 재시도 로직 (autoretry_for, retry_backoff)
- [ ] serializers.py (DRF 시리얼라이저)
- [ ] views.py (API 뷰)
  - POST /api/scrape/ - 스크래핑 요청
  - GET /api/scrape/ - 작업 목록 조회
  - GET /api/scrape/{id}/ - 개별 작업 조회
- [ ] urls.py (URL 라우팅)

### 4. 스케줄링 설정 (django-celery-beat)
- [ ] settings.py에 django_celery_beat 앱 추가
- [ ] migrate로 beat 테이블 생성 (PeriodicTask, IntervalSchedule 등)
- [ ] scraper/views.py에 스케줄 API 추가
  - POST /api/schedule/ - 스케줄 등록 (IntervalSchedule + PeriodicTask 생성)
  - GET /api/schedule/ - 스케줄 목록 조회
  - PATCH /api/schedule/{id}/ - 스케줄 수정 (활성화/비활성화)
  - DELETE /api/schedule/{id}/ - 스케줄 삭제
- [ ] Django Admin에서도 스케줄 관리 가능

### 5. 프론트엔드 구성 (Node.js + Express)
- [ ] Dockerfile 작성
- [ ] package.json (express)
- [ ] server.js (Express 정적 파일 서버)
- [ ] public/index.html (메인 페이지)
- [ ] public/css/style.css (스타일)
- [ ] public/js/app.js (API 호출 및 UI 로직)

### 6. API 명세

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | /api/scrape/ | URL 스크래핑 요청 (단일/다중) |
| GET | /api/scrape/ | 전체 작업 목록 조회 |
| GET | /api/scrape/{id}/ | 개별 작업 상태/결과 조회 |
| POST | /api/schedule/ | 스케줄 등록 |
| GET | /api/schedule/ | 스케줄 목록 조회 |
| PATCH | /api/schedule/{id}/ | 스케줄 수정 (활성화/비활성화) |
| DELETE | /api/schedule/{id}/ | 스케줄 삭제 |

### 7. 실행 방법

#### 프로덕션 (전체 Docker)
```bash
docker-compose up --build
```
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- Flower (모니터링): http://localhost:5555

#### 개발 환경 (로컬 + Docker 인프라)
```bash
# 1. DB, Redis만 Docker로 실행
docker-compose -f docker-compose.dev.yml up -d

# 2. 백엔드 가상환경 설정
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 3. 마이그레이션
python manage.py migrate

# 4. VSCode에서 F5로 디버깅 시작
```

---

## 개발 환경 설정 (VSCode 디버깅)

### docker-compose.dev.yml
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: scraper
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_dev_data:
```

### .vscode/launch.json
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Django",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/backend/manage.py",
      "args": ["runserver", "0.0.0.0:8000", "--noreload"],
      "django": true,
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DEBUG": "True",
        "DATABASE_URL": "postgres://postgres:postgres@localhost:5432/scraper",
        "REDIS_URL": "redis://localhost:6379/0"
      }
    },
    {
      "name": "Celery Worker",
      "type": "debugpy",
      "request": "launch",
      "module": "celery",
      "args": ["-A", "config", "worker", "-l", "DEBUG", "--pool=solo"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DEBUG": "True",
        "DATABASE_URL": "postgres://postgres:postgres@localhost:5432/scraper",
        "REDIS_URL": "redis://localhost:6379/0"
      }
    },
    {
      "name": "Celery Beat",
      "type": "debugpy",
      "request": "launch",
      "module": "celery",
      "args": ["-A", "config", "beat", "-l", "DEBUG", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DEBUG": "True",
        "DATABASE_URL": "postgres://postgres:postgres@localhost:5432/scraper",
        "REDIS_URL": "redis://localhost:6379/0"
      }
    }
  ],
  "compounds": [
    {
      "name": "Django + Celery",
      "configurations": ["Django", "Celery Worker", "Celery Beat"]
    }
  ]
}
```

### 개발 환경 구성도
```
┌─────────────────────────────────────────────────────────┐
│                    로컬 (VSCode 디버깅)                   │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Django    │  │   Celery    │  │   Celery    │     │
│  │  (F5 실행)  │  │   Worker    │  │    Beat     │     │
│  │  :8000      │  │  (F5 실행)  │  │  (F5 실행)  │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────┐
│                     Docker                              │
│                          │                              │
│         ┌────────────────┴────────────────┐             │
│         ▼                                 ▼             │
│  ┌─────────────┐                   ┌─────────────┐     │
│  │ PostgreSQL  │                   │    Redis    │     │
│  │   :5432     │                   │   :6379     │     │
│  └─────────────┘                   └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 데이터 모델

### ScrapeTask (즉시 실행)
| 필드 | 타입 | 설명 |
|------|------|------|
| id | AutoField | PK |
| url | URLField | 스크래핑 대상 URL |
| status | CharField | pending / running / completed / failed |
| result | JSONField | 스크래핑 결과 |
| error_message | TextField | 에러 메시지 (실패 시) |
| created_at | DateTimeField | 생성 시간 |
| updated_at | DateTimeField | 수정 시간 |
