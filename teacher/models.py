from django.db import models
from datetime import timedelta
# Create your models here.

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User


class LearningPath(models.Model):
    PRIMARY = 'PR'
    UPPER = 'UP'
    LOWER = 'LO'
    GYM = 'GY'

    
    SCHOOL_LEVEL_CHOICES = [
        (PRIMARY, 'Primary School'),
        (UPPER, 'Upper Secondary School'),
        (LOWER, 'Lower Secondary School'),
        (GYM, 'Gymnasium'),
    ]
    
    
    
    # Subject choices (can be expanded as needed)
    MATH = 'MA'
    SCIENCE = 'SC'
    ENGLISH = 'EN'
    HISTORY = 'HI'
    COMPUTER_SCIENCE = 'CS'
    ART = 'AR'
    MUSIC = 'MU'
    
    SUBJECT_CHOICES = [
        (MATH, 'Mathematics'),
        (SCIENCE, 'Science'),
        (ENGLISH, 'English'),
        (HISTORY, 'History'),
        (COMPUTER_SCIENCE, 'Computer Science'),
        (ART, 'Art'),
        (MUSIC, 'Music'),
    ]
    
    # Main fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    school_level = models.CharField(
        max_length=2,
        choices=SCHOOL_LEVEL_CHOICES,
        default=PRIMARY,
    )
    subject = models.CharField(
        max_length=2,
        choices=SUBJECT_CHOICES,
        default=MATH,
    )
    topics = models.CharField(max_length=200)  # Could be a comma-separated list or consider ManyToMany
    sub_topics = models.CharField(max_length=300)  # Could be a comma-separated list or consider ManyToMany
    learning_outcomes = models.TextField()
    owner = models.ForeignKey(
        User,  # or your custom user model
        on_delete=models.CASCADE,
        related_name='learning_paths',
        null=True,  # Optional: set to False if owner is required
        blank=True  # Optional: set to False if owner is required
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

    def get_total_time(self):
        """
        Calculate the total approximate time for this learning path
        by summing all tasks' approximate_time from all episodes.
        Returns the total time in minutes (or whatever unit you're using).
        """
        total_time = timedelta()
        
        # Iterate through all episodes in this learning path
        for episode in self.episodes.all():
            # Sum all tasks' approximate_time in this episode
            episode_time = episode.learning_tasks.aggregate(
                total=models.Sum('approximate_time')
            )['total'] or 0
            
            total_time += episode_time
            
        return total_time
    
    def get_total_tasks(self):
        """
        Calculate the total approximate time for this learning path
        by summing all tasks' approximate_time from all episodes.
        Returns the total time in minutes (or whatever unit you're using).
        """
        total_tasks = 0
        
        # Iterate through all episodes in this learning path
        for episode in self.episodes.all():
            # Sum all tasks' approximate_time in this episode
            tasks = episode.learning_tasks.aggregate(
                total=models.Count('id')
            )['total'] or 0
            total_tasks += tasks
            
        return total_tasks
    
    def get_task_type_counts(self):
        """
        Returns a dictionary with counts of each task type in this learning path.
        Example return value: {'IND': 5, 'GRP': 3, 'WHOLE': 2}
        """
        from django.db.models import Count
        
        # Get all tasks in this learning path through episodes
        tasks = LearningTask.objects.filter(episode__learning_path=self)
        
        # Annotate counts for each task type
        type_counts = tasks.values('task_type').annotate(count=Count('task_type'))
        
        # Convert to a dictionary {task_type: count}
        result = {item['task_type']: item['count'] for item in type_counts}
        
        # Ensure all task types are represented, even if count is 0
        for task_type in dict(LearningTask.TASK_TYPE_CHOICES).keys():
            if task_type not in result:
                result[task_type] = 0
        
        return result

    class Meta:
        verbose_name = "Learning Path"
        verbose_name_plural = "Learning Paths"

class LearningSession(models.Model):
    # Reuse the same choices from LearningPath for consistency
    SCHOOL_LEVEL_CHOICES = LearningPath.SCHOOL_LEVEL_CHOICES
    
    # Main fields
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='learning_sessions'
    )
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_learning_sessions'
    )
    school_level = models.CharField(
        max_length=2,
        choices=SCHOOL_LEVEL_CHOICES,
        default=LearningPath.PRIMARY,
    )
    #target_class = models.CharField(max_length=100)  # Could be "Grade 5" or "Class 10B" etc.
    #school = models.CharField(max_length=200)  # Name of the school/institution
    label = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.label} - {self.learning_path.title}"
    
    class Meta:
        verbose_name = "Learning Session"
        verbose_name_plural = "Learning Sessions"
        ordering = ['-created_at']

class Episode(models.Model):
    KNOWBIT_CHOICES = [
        ('KB1', 'Knowbit 1'),
        ('KB2', 'Knowbit 2'),
        ('KB3', 'Knowbit 3'),
        # Add more as needed
    ]
    
    SKILLBIT_CHOICES = [
        ('SB1', 'Skillbit 1'),
        ('SB2', 'Skillbit 2'),
        ('SB3', 'Skillbit 3'),
        # Add more as needed
    ]

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    knowbits = models.CharField(max_length=200, choices=KNOWBIT_CHOICES, blank=True)
    skillbits = models.CharField(max_length=200, choices=SKILLBIT_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sequence_number = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.sequence_number is None:
            last_seq = Episode.objects.filter(learning_path=self.learning_path).aggregate(models.Max('sequence_number'))['sequence_number__max']
            self.sequence_number = (last_seq or 0) + 1
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sequence_number']

    def __str__(self):
        return f"{self.sequence_number}. {self.title}"


class LearningTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('IND', 'Individual'),
        ('GRP', 'Group'),
        ('WHOLE', 'Whole Class'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('LOW', 'Low'),
        ('MED', 'Medium'),
        ('HIGH', 'High'),
    ]

    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='learning_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=5, choices=TASK_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    approximate_time = models.DurationField()
    difficulty_level = models.CharField(max_length=4, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Resource(models.Model):
    learning_task = models.ForeignKey(LearningTask, on_delete=models.CASCADE, related_name='resources')
    h5p = models.URLField(max_length=500,null=True, blank=True)
    url = models.URLField(max_length=500,null=True, blank=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return f"Resource for {self.learning_task.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_on = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'learning_path')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.learning_path}"


admin.site.register(Episode)
admin.site.register(LearningTask)
admin.site.register(LearningPath)
admin.site.register(Resource)
admin.site.register(Enrollment)