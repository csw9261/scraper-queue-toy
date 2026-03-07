from rest_framework import serializers

from .models import ScrapeTask


# POST /api/tasks/ 요청 시 사용 — url 필드만 입력받음
class ScrapeTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeTask
        fields = ["url"]


# GET 응답 시 사용 — 전체 필드 반환
class ScrapeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeTask
        fields = ["id", "url", "status", "result", "error_message", "created_at", "updated_at"]
