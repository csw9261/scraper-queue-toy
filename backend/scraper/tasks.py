import requests
from bs4 import BeautifulSoup
from celery import shared_task

from .models import ScrapeTask


# autoretry_for: 어떤 예외가 발생하면 자동 재시도할지 지정
# max_retries: 최대 재시도 횟수
# retry_backoff: True면 재시도 간격을 점점 늘림 (1초 → 2초 → 4초)
@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def scrape_url(task_id):
    task = ScrapeTask.objects.get(id=task_id)

    # 작업 시작 — 상태를 running으로 변경
    task.status = "running"
    task.save(update_fields=["status", "updated_at"])

    try:
        # URL fetch (10초 안에 응답 없으면 timeout 예외 발생)
        response = requests.get(task.url, timeout=10)
        # 4xx, 5xx 응답이면 예외 발생
        response.raise_for_status()

        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # <title> 태그 텍스트 추출
        title = soup.title.string.strip() if soup.title else None
        # 첫 번째 <h1> 태그 텍스트 추출
        h1 = soup.find("h1")
        h1_text = h1.get_text(strip=True) if h1 else None
        # <meta name="description"> content 추출
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc and meta_desc.get("content") else None

        # 결과 저장 후 completed로 변경
        task.result = {
            "title": title,
            "h1": h1_text,
            "description": description,
        }
        task.status = "completed"
        task.save(update_fields=["status", "result", "updated_at"])

    except Exception as exc:
        # 실패 시 에러 메시지 저장 후 failed로 변경
        task.error_message = str(exc)
        task.status = "failed"
        task.save(update_fields=["status", "error_message", "updated_at"])
        # 예외를 다시 발생시켜야 Celery가 재시도를 트리거함
        raise exc
