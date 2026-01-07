from django.db import models

class ScrapeTask(models.Model):
    # 상태값 정의
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # 작업 대기
        ('running', 'Running'),      # 작업 중
        ('completed', 'Completed'),  # 완료
        ('failed', 'Failed'),       # 실패
    ]

    url = models.URLField(max_length=500)             # 스크래핑할 주소
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)   # 스크래핑 결과 (제목, 내용 등 JSON 형식)
    error_message = models.TextField(null=True, blank=True) # 에러 발생 시 내용 저장
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.url} - {self.status}"