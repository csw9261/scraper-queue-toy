import os
from celery import Celery

# Django의 세팅 모듈을 Celery의 기본 세팅 모듈로 설정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('scraper_queue')

# 여기서 namespace='CELERY'는 모든 셀러리 관련 설정 키가 'CELERY_'로 시작해야 함을 의미합니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 등록된 모든 앱에서 tasks.py를 자동으로 찾습니다.
app.autodiscover_tasks()
