# Create your views here.
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from student.models import TaskInteraction
from teacher.models import LearningPath, Enrollment, LearningSession
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.utils import timezone


from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import Profile, StudentProfile
from .forms import StudentProfileUpdateForm
from users.forms import UpdateProfileForm, UpdateUserForm
from django.contrib.auth.models import User


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
        return render(request, 'learning_path.html', context)

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

        sessions = LearningSession.objects.all()

        # Get in-progress tasks
        in_progress_tasks = TaskInteraction.objects.filter(
            student=student,
            status='in_progress'
        ).select_related('task', 'task__episode', 'task__episode__learning_path')

        context = {
            'enrollments': enrollments,
            'in_progress_tasks': in_progress_tasks,
            'sessions':sessions
        }
        return render(request, 'dashboard.html', context)

class TaskView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'task_element.html',{})
    
class StudentProfileDetailView(LoginRequiredMixin, DetailView):
    model = StudentProfile
    template_name = 'profile_view.html'
    context_object_name = 'student_profile'

    def get_object(self):
        return self.request.user

class StudentProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'update_student_profile.html'
    success_url = reverse_lazy('session_list')
    success_message = "Your profile has been updated successfully!"

    def get_object(self, queryset=None):
        # Get or create student profile for the current user
        profile = Profile.objects.get(user=self.request.user)
        student_profiles = StudentProfile.objects.filter(profile = profile)

        if len(student_profiles) == 0:
            profile = Profile.objects.get(user=self.request.user)
            student_profile = StudentProfile.objects.create(profile=profile,school_level=StudentProfile.HIGH_SCHOOL,
                                                            school_name='',
                                                            current_class='')

        return self.request.user.profile.studentprofile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['u_form'] = UpdateUserForm(instance=self.request.user)
        context['p_form'] = UpdateProfileForm(instance=self.request.user.profile)
        return context

    def get_form_class(self):
        return StudentProfileUpdateForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        u_form = UpdateUserForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        sp_form = self.get_form()

        if u_form.is_valid() and p_form.is_valid() and sp_form.is_valid():
            u_form.save()
            p_form.save()
            return self.form_valid(sp_form)
        else:
            return self.form_invalid(sp_form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)