# Scraper Queue Toy Project

Django, Celery, Redis를 기반으로 한 비동기 웹 스크래퍼 토이 프로젝트입니다.

## 기술 스택 및 사용 라이브러리

- **Django**: 메인 웹 프레임워크. 데이터 모델링 및 관리 UI 제공.
- **Celery**: 비동기 작업 큐. 대량의 URL 스크래핑 작업을 백그라운드에서 처리.
- **Redis**: 메시지 브로커 및 결과 백엔드. Django와 Celery 사이의 통신 담당.
- **django-celery-results**: Celery 작업 결과를 Django DB에 저장하고 조회하기 위한 확장.
- **Requests**: 웹 페이지 콘텐츠를 가져오기 위한 HTTP 라이브러리.
- **BeautifulSoup4**: HTML 파싱 및 데이터 추출을 위한 라이브러리.
- **Flower**: Celery 클러스터를 위한 실시간 모니터링 및 웹 관리 툴.

## 설치 및 실행 (예정)

1. 가상환경 활성화
2. 패키지 설치: `pip install -r requirements.txt`
3. Redis 실행 (Docker 권장)
4. Django 마이그레이션: `python manage.py migrate`
5. 서버 실행: `python manage.py runserver`
6. Celery 워커 실행: `celery -A config worker -l info`
7. Flower 실행: `celery -A config flower`
