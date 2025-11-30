from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "ok", "message": "Task Analyzer API is running!"})

urlpatterns = [
    path('', home),  # ← This fixes the 404 root URL
    path('admin/', admin.site.urls),
    path('api/tasks/', include('tasks.urls')),
]
