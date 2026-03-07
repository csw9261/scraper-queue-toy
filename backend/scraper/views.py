from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import ScrapeTask
from .serializers import ScrapeTaskSerializer, ScrapeTaskCreateSerializer
from .tasks import scrape_url


@api_view(["GET", "POST"])
def task_list(request):
    if request.method == "GET":
        tasks = ScrapeTask.objects.all().order_by("-created_at")
        serializer = ScrapeTaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ScrapeTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            scrape_url.delay(task.id)
            return Response(ScrapeTaskSerializer(task).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def task_detail(request, pk):
    try:
        task = ScrapeTask.objects.get(pk=pk)
    except ScrapeTask.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScrapeTaskSerializer(task)
    return Response(serializer.data)
