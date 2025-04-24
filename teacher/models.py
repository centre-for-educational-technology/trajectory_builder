from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class LearningPath(models.Model):
    # School level choices
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
        default=HIGH_SCHOOL,
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
    
    class Meta:
        verbose_name = "Learning Path"
        verbose_name_plural = "Learning Paths"



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
    sequence_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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