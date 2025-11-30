from django.db import models
import uuid

class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    importance = models.IntegerField(default=5)  # 1-10
    dependencies = models.JSONField(default=list, blank=True)  # list of task IDs (strings)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
