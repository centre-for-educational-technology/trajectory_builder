# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from datetime import timedelta
from teacher.models import LearningPath, Episode, LearningTask, Resource, LearningSession
from django.utils import timezone
from users.models import Profile
from django.contrib import admin

class StudentProfile(models.Model):
    """Extends Profile with school and class information"""
    # School level choices (similar to your LearningPath)
    ELEMENTARY = 'EL'
    MIDDLE_SCHOOL = 'MS'
    HIGH_SCHOOL = 'HS'
    COLLEGE = 'CO'
    UNIVERSITY = 'UN'
    OTHER = 'OT'
    
    SCHOOL_LEVEL_CHOICES = [
        (ELEMENTARY, 'Elementary School'),
        (MIDDLE_SCHOOL, 'Middle School'),
        (HIGH_SCHOOL, 'High School'),
        (COLLEGE, 'College'),
        (UNIVERSITY, 'University'),
        (OTHER, 'Other'),
    ]
    
    school_level = models.CharField(
        max_length=2,
        choices=SCHOOL_LEVEL_CHOICES,
        default=HIGH_SCHOOL,
    )
    # one-to-one mapping with Django User model
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    school_name = models.CharField(max_length=200)
    current_class = models.CharField(max_length=100)  # e.g. "Grade 5" or "Class 10B"
    
    def __str__(self):
        return f"{self.user.username}'s Student Profile"

class TaskInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_interactions')
    task = models.ForeignKey(LearningTask, on_delete=models.CASCADE, related_name='interactions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    learning_session = models.ForeignKey(
        LearningSession,  # Using string reference if in same app, or 'app_name.LearningSession'
        on_delete=models.CASCADE,
        related_name='task_interactions'
    )
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='not_started')
    score = models.FloatField(null=True, blank=True)  # Optional for performance tracking

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['learning_session', 'task', 'student'],
                name='unique_task_interaction_per_session'
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.task} ({self.status})"
    
    @classmethod
    def get_student_session_interactions(cls, student_id, learning_session_id):
        """Get all interactions for a student in a specific session"""
        return cls.objects.filter(
            student_id=student_id,
            task__episode__learning_path__learning_sessions=learning_session_id
        ).select_related('task__episode')
    
    @classmethod
    def get_stats_for_student_session(cls, student_id, learning_session_id):
        """Get enhanced statistics with time tracking"""
        interactions = cls.objects.filter(
            student_id=student_id,
            task__episode__learning_path__learning_sessions=learning_session_id
        ).select_related('task')
        
        # Basic completion stats
        
        completed_tasks = interactions.filter(status='completed')
        in_progress_tasks = interactions.filter(status='in_progress')
        
        # Time calculations
        time_metrics = cls.calculate_time_metrics(interactions, completed_tasks, in_progress_tasks)
        
        return {
            'interactions': interactions,
            'stats': {
                'completed_tasks': completed_tasks.count(),
                'in_progress_tasks': in_progress_tasks.count(),
                **time_metrics
            }
        }
    
    @classmethod
    def calculate_time_metrics(cls, interactions, completed_tasks, in_progress_tasks):
        """Helper method for time calculations"""
        
        
        completed_time = completed_tasks.annotate(
            duration=ExpressionWrapper(
                F('completed_at') - F('started_at'),
                output_field=DurationField()
            )
        ).aggregate(
            total_spent=Sum('duration')
        )['total_spent'] or timedelta()
        
        in_progress_time = in_progress_tasks.annotate(
            current_duration=ExpressionWrapper(
                timezone.now() - F('started_at'),
                output_field=DurationField()
            )
        ).aggregate(
            total_current=Sum('current_duration')
        )['total_current'] or timedelta()
        

        
        return {
            'time_metrics': {
                'total_time_spent': completed_time + in_progress_time,
                'completed_time_spent': completed_time,
                'in_progress_time_spent': in_progress_time,
            }
        }


class ResourceInteraction(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_interactions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='interactions')
    viewed_on = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(null=True, blank=True)  # Optional: 1-5 rating

    def __str__(self):
        return f"{self.student.username} viewed {self.resource}"

admin.site.register(TaskInteraction)