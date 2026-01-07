# 프로젝트 진행 현황 (Progress Check)

## 단계 1: 프로젝트 기초 및 인프라 설정
- [x] 프로젝트 디렉토리 생성 (backend/, frontend/)
- [x] Docker 설정 파일 작성 (docker-compose.yml, docker-compose.dev.yml)
- [x] 백엔드 패키지 설정 (requirements.txt, Dockerfile)
- [x] Django 프로젝트 초기화 (startproject, startapp)
- [x] Django 기본 설정 수정 (settings.py, celery.py, __init__.py)

---

## 단계 2: 백엔드 핵심 기능 구현 (현재 단계)

### Step 1: DB 모델 정의 (scraper/models.py)
- [x] 스크래핑 상태(대기/실행/완료/실패) 필드 구성
- [x] 결과 데이터(JSON) 저장 필드 구성
- [x] 생성/수정 시간 필드 구성
- **확인 사항:** models.py 코드 리뷰 및 확정 (완료)

### Step 2: 스크래핑 로직 구현 (scraper/tasks.py)
- [ ] Celery 태스크 정의
- [ ] BeautifulSoup 기반 크롤링 로직 작성
- [ ] 성공/실패 시 DB 상태 업데이트 로직
- **확인 사항:** 실제 스크래핑 로직 작동 방식 확인

### Step 3: API 및 시리얼라이저 작성
- [ ] serializers.py: DB 데이터를 JSON으로 변환
- [ ] views.py: 요청을 받고 태스크를 실행하는 API 로직
- [ ] urls.py: API 엔드포인트 연결 (/api/scrape/)
- **확인 사항:** API 명세(Input/Output) 확인