# Create your views here.
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from student.models import TaskInteraction
from teacher.models import LearningPath, LearningTask, Episode, Enrollment

from django.shortcuts import get_object_or_404
from django.utils import timezone

class LearningPathDetailView(LoginRequiredMixin, View):
    def get(self, request, path_id, episode_index=0, task_index=0):
        student = request.user
        learning_path = get_object_or_404(LearningPath, id=path_id)
        episodes = learning_path.episodes.all().order_by('sequence_number')

        if episode_index >= len(episodes):
            return render(request, 'students/learning_complete.html', {'learning_path': learning_path})

        current_episode = episodes[episode_index]
        tasks = list(current_episode.learning_tasks.all().order_by('id'))

        if task_index >= len(tasks):
            # move to next episode
            return redirect('students:learning_path', path_id=path_id, episode_index=episode_index + 1, task_index=0)

        current_task = tasks[task_index]

        # Check or create task interaction
        interaction, created = TaskInteraction.objects.get_or_create(
            student=student,
            task=current_task,
            defaults={'status': 'in_progress'}
        )

        context = {
            'learning_path': learning_path,
            'current_episode': current_episode,
            'current_task': current_task,
            'interaction': interaction,
            'episode_index': episode_index,
            'task_index': task_index,
        }
        return render(request, 'students/learning_path.html', context)

    def post(self, request, path_id, episode_index=0, task_index=0):
        action = request.POST.get('action')
        student = request.user
        learning_path = get_object_or_404(LearningPath, id=path_id)
        episodes = learning_path.episodes.all().order_by('sequence_number')
        current_episode = episodes[episode_index]
        tasks = list(current_episode.learning_tasks.all().order_by('id'))
        current_task = tasks[task_index]

        if action == 'complete':
            interaction = TaskInteraction.objects.get(student=student, task=current_task)
            interaction.status = 'completed'
            interaction.completed_at = timezone.now()
            interaction.save()

        # move to next task (or next episode handled in GET)
        return redirect('students:learning_path', path_id=path_id, episode_index=episode_index, task_index=task_index + 1)


class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        student = request.user

        # Get all enrollments
        enrollments = Enrollment.objects.filter(student=student)

        # Get in-progress tasks
        in_progress_tasks = TaskInteraction.objects.filter(
            student=student,
            status='in_progress'
        ).select_related('task', 'task__episode', 'task__episode__learning_path')

        context = {
            'enrollments': enrollments,
            'in_progress_tasks': in_progress_tasks,
        }
        return render(request, 'dashboard.html', context)
