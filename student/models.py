# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from teacher.models import LearningPath, Episode, LearningTask, Resource


class TaskInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_interactions')
    task = models.ForeignKey(LearningTask, on_delete=models.CASCADE, related_name='interactions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='not_started')
    score = models.FloatField(null=True, blank=True)  # Optional for performance tracking

    def __str__(self):
        return f"{self.student.username} - {self.task} ({self.status})"


class ResourceInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_interactions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='interactions')
    viewed_on = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(null=True, blank=True)  # Optional: 1-5 rating

    def __str__(self):
        return f"{self.student.username} viewed {self.resource}"
