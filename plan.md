# 웹 스크래퍼 토이 프로젝트 계획 (Django + Celery + Redis)

## 1. 환경 설정 (Environment Setup)
- 가상 환경 생성 및 활성화
- 필수 패키지 설치: `django`, `celery`, `redis`, `django-celery-results`, `requests`, `beautifulsoup4`, `flower`
- Django 프로젝트 및 앱(`scraper`) 생성

## 2. 인프라 구성 (Infrastructure - Redis)
- Redis를 메시지 브로커 및 결과 백엔드로 설정
- Docker를 사용하여 Redis 실행 권장: `docker run -d -p 6379:6379 redis`

## 3. Django 설정 (Configuration)
- `settings.py`에 Celery 설정 추가 (Broker URL, Result Backend 등)
- 프로젝트 설정 폴더에 `celery.py` 생성 및 Celery 앱 인스턴스화

## 4. 데이터 모델링 (Data Modeling)
- `scraper/models.py`에 `ScrapeItem` 모델 생성
    - `url`: 스크래핑 대상 URL
    - `status`: 상태 (대기중, 진행중, 완료, 실패)
    - `result`: 스크래핑 결과 데이터 (JSON 또는 텍스트)
    - `error_message`: 실패 시 에러 메시지
    - `created_at`, `updated_at`: 타임스탬프

## 5. Celery 태스크 구현 (Task Implementation)
- `scraper/tasks.py` 생성
- `requests`와 `BeautifulSoup`을 이용한 스크래핑 로직 구현
- **재시도 로직(Retry Logic)**: 네트워크 에러나 일시적인 오류 발생 시 자동 재시도 (`autoretry_for`, `retry_backoff` 활용)
- 태스크 진행 상황에 따른 데이터베이스 상태 업데이트

## 6. 뷰 및 URL 구성 (Views & URLs)
- **URL 등록 페이지**: 스크래핑할 URL(들)을 입력받아 Celery 태스크로 전달하는 기능 (대량 처리를 위해 텍스트 영역 사용)
- **결과 목록 페이지**: 요청한 스크래핑 작업들의 상태와 결과를 확인

## 7. 모니터링 (Flower)
- Flower를 통한 Celery 워커 및 태스크 실시간 모니터링
- 실행: `celery -A <project_name> flower`

## 8. 실행 및 테스트 단계
1. Redis 서버 실행
2. Django 마이그레이션 (`migrate`)
3. Django 서버 실행 (`runserver`)
4. Celery 워커 실행 (`worker`)
5. Flower 실행 (`flower`)
6. 대량의 URL을 입력하여 큐 처리 및 재시도 로직 동작 확인
