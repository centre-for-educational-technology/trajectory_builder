# Create your views here.
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from student.models import TaskInteraction
from teacher.models import Enrollment, LearningSession, LearningTask, Episode
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, F, ExpressionWrapper, DurationField

from datetime import timedelta
from django.contrib import messages

from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from .models import Profile, StudentProfile
from .forms import StudentProfileUpdateForm
from users.forms import UpdateProfileForm, UpdateUserForm
from django.contrib.auth.models import User

def get_episode_metrics_dict(learning_session, student):
    """
    Get information on students' progress on learning path
    """
    metrics = []
    
    episodes = Episode.objects.filter(
        learning_path=learning_session.learning_path
    ).order_by('sequence_number')
    
    for episode in episodes:
        # Calculate time spent on completed tasks in this episode
        time_spent = TaskInteraction.objects.filter(
            learning_session=learning_session,
            task__episode=episode,
            status='completed',
            student=student.id
        ).aggregate(
            total_time=Sum(F('completed_at') - F('started_at'))
        )['total_time'] or timedelta(0)
        
        # Count completed tasks in this episode
        completed_count = TaskInteraction.objects.filter(
            learning_session=learning_session,
            task__episode=episode,
            status='completed',
            student=student.id
        ).count()

        # Count completed tasks in this episode
        in_progress_count = TaskInteraction.objects.filter(
            learning_session=learning_session,
            task__episode=episode,
            status='in_progress',
            student=student.id
        ).count()
        
        # Total tasks in episode
        total_tasks = episode.learning_tasks.count()

        print("In progress:",in_progress_count)

        # badge
        episode_status = None
        if completed_count == total_tasks:
            episode_status = 'completed'
        elif in_progress_count > 0:
            episode_status = "in-progress"
        else:
            episode_status = "not-started"
        
        metrics.append({
            'episode_id': episode.id,
            'episode_title': episode.title,
            'episode_description':episode.description,
            'sequence_number': episode.sequence_number,
            'total_time_spent': time_spent,
            'tasks_completed': completed_count,
            'total_tasks': total_tasks,
            'episode_status':episode_status,
            'completion_percentage': round((completed_count / total_tasks * 100) if total_tasks else 0, 2)
        })
    return metrics


class LearningPathStudentView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        student = request.user
        learning_session = get_object_or_404(LearningSession, id=session_id)
        learning_path = learning_session.learning_path
        episodes = learning_path.episodes.all().order_by('sequence_number')

        # Get all task interactions for this student in this learning path
        interactions = TaskInteraction.objects.filter(learning_session=learning_session, student=self.request.user)

        completed = interactions.filter(status='completed')

        total_tasks = learning_path.get_total_tasks()

        print('Total tasks:',total_tasks)

        total_time = learning_path.get_total_time()

        # Determine current progress and next task
        current_task = self._determine_current_task(episodes, interactions)

        # Time calculations
        total_time_spent = interactions.aggregate(
            total=Sum(F('completed_at') - F('started_at'), output_field=DurationField())
        )['total'] or timedelta()

        remaining_time = total_time - total_time_spent
        
        if current_task is not None:
            # Get or create interaction for current task
            interaction, created = TaskInteraction.objects.get_or_create(
                student=student,
                task=current_task,
                learning_session=learning_session,
                defaults={'status': 'not_started'}
            )
        
        # Data for learning path visualization
        learning_path_progress = get_episode_metrics_dict(learning_session, student)

        # Learning path tasks type count
        task_counts = learning_path.get_task_type_counts()


        context = {
            'learning_path': learning_path,
            'learning_session':learning_session,
            'current_task': current_task,
            'total_time':total_time,
            'total_tasks':total_tasks,
            'completed_tasks':len(interactions.filter(status='completed')),
            'completion_percentage':(len(completed) * 100/total_tasks),
            'total_time_spent':total_time_spent,
            'remaining_time':0 if (remaining_time < timedelta(0)) else remaining_time,
            'learning_path_progress':learning_path_progress,
            'task_counts':task_counts
        }
        return render(request, 'learning_path.html', context)
    
    def _determine_current_task(self, episodes, interactions):
        """Determine which task should be presented to the student next"""
        # Find first incomplete task based on interaction status
        for episode in episodes:
            for task in episode.learning_tasks.order_by('id'):
                interaction = interactions.filter(task=task).first()
                if not interaction or interaction.status != 'completed':
                    return task
        return None



class StudentDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        student = request.user

        # Get all enrollments
        enrollments = Enrollment.objects.filter(student=student)

        sessions = LearningSession.objects.all()

        sessions_extends = []

        interactions = TaskInteraction.objects.filter(student=self.request.user).exclude(status ='completed').order_by('-started_at')
        current_task = None
        current_session = None
        context = {}

        if len(interactions) != 0:
            interaction = interactions.first()
            current_task = interaction.task
            current_session = interaction.learning_session
            context['current_task'] = current_task
            context['current_session'] = current_session

        for session in sessions:
            session_dict = {'object':session}

            interactions = TaskInteraction.objects.filter(learning_session=session, student=self.request.user,status='completed')
            session_dict['completed'] = len(interactions)
            session_dict['total_time'] = session.learning_path.get_total_time()
            session_dict['total_tasks'] = session.learning_path.get_total_tasks()
            session_dict['completion_percentage'] = (len(interactions) * 100/session_dict['total_tasks'])
            session_dict['enrolled'] = 1

            sessions_extends.append(session_dict)

            if current_session is not None and current_session == session:
                context['current_session_completed'] = session_dict['completed']
                context['current_session_total'] = session_dict['total_tasks']

        context['sessions_extends'] =sessions_extends
        
        return render(request, 'dashboard.html', context)

class TaskView(LoginRequiredMixin, View):
    def get(self, request, session_id, task_id):
        learning_session = get_object_or_404(LearningSession, id=session_id)
        learning_path = learning_session.learning_path

        current_task = LearningTask.objects.get(id=task_id)

        # Get or create interaction for current task
        interaction, created = TaskInteraction.objects.get_or_create(
            student=self.request.user,
            task=current_task,
            learning_session=learning_session
        )

        if not created:
            interaction.status = 'in_progress'
            interaction.save()

        context = {
            'task':current_task,
            'learning_session':learning_session,
            'interaction':interaction
        }

        return render(request, 'task_element.html',context)
    
    def post(self, request, *args, **kwargs):
        # Get form data
        interaction_id = request.POST.get('interaction_id')
        task_id = request.POST.get('task_id')
        session_id = request.POST.get('session_id')
            
        # Validate required fields
        if not interaction_id or not task_id or not session_id:
            raise ValueError("Missing required fields")
            
        # Get objects with permission check
        interaction = get_object_or_404(
            TaskInteraction,
            id=interaction_id,
            student=request.user  # Ensure user owns this interaction
        )

        learning_session = get_object_or_404(LearningSession,
                                          id=session_id)
            
        task = get_object_or_404(
            LearningTask,
            id=task_id
        )
            
        # Update the interaction
        interaction.status = 'completed'
        interaction.completed_at = timezone.now()
        interaction.save()
            
        # messages.success(request, f'Task "{task.title}" marked as completed!')

        episodes = learning_session.learning_path.episodes.all().order_by('sequence_number')

        

        # Get all task interactions for this student in this learning path
        interactions = TaskInteraction.objects.filter(learning_session=learning_session, 
                                                      student=self.request.user)
    
        # Determine current progress and next task
        current_task = self._determine_current_task(episodes, interactions)

        if current_task is None:
            return redirect('learning_path',session_id=learning_session.id)
        else:

            return redirect('learning_path_task',session_id=learning_session.id,task_id=current_task.id)

    def _determine_current_task(self, episodes, interactions):
        """Determine which task should be presented to the student next"""
        # Find first incomplete task based on interaction status
        for episode in episodes:
            for task in episode.learning_tasks.order_by('id'):
                interaction = interactions.filter(task=task).first()
                if not interaction or interaction.status != 'completed':
                    return task
        return None



    
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