# Create your views here.
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import LearningPath
from .forms import LearningPathForm
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Episode, LearningTask, Resource, LearningSession
import requests
from django.contrib.auth.models import User
from django.contrib import messages

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from .forms import LearningPathForm, ResourceForm, EpisodeForm, LearningTaskForm, LearningSessionForm, RegistrationToggleForm
from .models import LearningPath, Episode, LearningTask, Resource, SessionRegistration, Enrollment
import uuid

from student.models import TaskInteraction

from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class StaffUserRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is_staff."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_staff:
            messages.add_message(request,messages.WARNING, f"You don't have permission to access {request.path}.")
            return redirect('student_dashboard')  # Or your preferred redirect
            
        return super().dispatch(request, *args, **kwargs)

@receiver(post_save, sender=LearningSession)
def create_session_registration(sender, instance, created, **kwargs):
    """
    Automatically creates a registration link when a new LearningSession is created
    """
    if created:
        SessionRegistration.objects.create(
            learning_session=instance,
            created_by=instance.created_by,
            code=uuid.uuid4(),
            is_active=True
        )


def get_session_analytics(learning_session):
    """
    Get information on students' progress on learning path

    Args:
    ----
        learning_session (LearningSession): Object of LearningSession model

    Returns:
    ----
        dict: Dictionary containing task completion status for each student
    """
    student_analytics = []
    
    learning_session_object = LearningSession.objects.select_related('learning_path').get(id=learning_session)

    # All enrolled students
    enrolled_students = Enrollment.objects.filter(learning_session=learning_session).select_related('student')

    # @todo: remove when enrollement workflow is added
    enrolled_students = User.objects.all()

    total_students = len(enrolled_students)

    episodes = Episode.objects.filter(learning_path = learning_session_object.learning_path).order_by('sequence_number')

    total_tasks = learning_session_object.learning_path.get_total_tasks()

    task_completed_all_students = 0

    episode_completed = 0
    total_episodes = len(learning_session_object.learning_path.episodes.all())

    header = []
    # Labeling info
    for ep_id,episode in enumerate(episodes):
        ep_id += 1
        tasks = LearningTask.objects.filter(episode=episode).order_by('id')

        for ts_id, task in enumerate(tasks):
            ts_id += 1
            header.append({'label':f'E{ep_id}-T{ts_id}', 'episode':episode, 'task':task})

    for student in enrolled_students:
        episode_analytics = []
        task_seq_new = 1
        for episode in episodes:
            task_analytics = {}
            tasks = LearningTask.objects.filter(episode=episode).order_by('id').all()

            episode_total_tasks = len(tasks)
            episode_task_completed = 0
            
            for seq, task in enumerate(tasks):
                task_analytics[task.id]='not-completed'

            interactions = TaskInteraction.get_student_episode_interactions(student,episode)

            for interaction in interactions:
                task_analytics[interaction.task.id] = interaction.status
                if interaction.status == 'completed':
                    task_completed_all_students += 1
                    episode_task_completed += 1
            
            print(f'Episode total:{episode_total_tasks} Completed:{episode_task_completed}')

            if episode_total_tasks == episode_task_completed:
                episode_completed += 1
            
            # Transforming dictionary into list
            task_records = [{"id": task_id, "status": status} for task_id, status in task_analytics.items()]
            episode_analytics.append({'episode':episode,'tasks':task_records})
        student_analytics.append({'id':student.id,'name':student.username, 'episodes':episode_analytics})
    avg_completed_episode_per_student = 0 if total_students == 0 else episode_completed/total_students
    avg_completed_tasks_per_student = 0 if ((total_students == 0) or (total_tasks == 0))  else (100 * task_completed_all_students)/(total_students*total_tasks)

    print('Episode completed:',episode_completed)

    return header,student_analytics,int(avg_completed_tasks_per_student),int(avg_completed_episode_per_student),total_episodes

class H5PProxySearchView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        print('Query:',query)
        if not query:
            return JsonResponse({'results': []})

        # Build the external API URL
        api_url = f'https://vara.h5p.ee/api/search-materials?q={query}' # Vara API call
        
        try:
            # Make the request with basic auth
            response = requests.get(api_url, auth=(settings.H5P_API_USER, settings.H5P_API_PASS))
            data = response.json()
            print('Obtained:',data)
            return JsonResponse({'results': data.get('materials', [])})
        except Exception as e:
            return JsonResponse({'results': [], 'error': str(e)}, status=500)


class LearningPathCreateView(LoginRequiredMixin, CreateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'trajectory_form.html'
    success_url = '/trajectory/list'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse('learning_path_config',kwargs={'pk':self.object.id})


class LearningSessionCreateView(LoginRequiredMixin, CreateView):
    model = LearningSession
    form_class = LearningSessionForm
    template_name = 'session_form.html'  # Reusing the same template
    # success_url = '/session/list'  # Not needed since we override get_success_url
    
    def get_form_kwargs(self):
        """Pass the request user to the form to filter learning paths"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Set the created_by user before saving"""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to the session detail page or configuration page"""
        return reverse('session_list')


class LearningSessionUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningSession
    form_class = LearningSessionForm
    template_name = 'session_form.html'
    
    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)
    
    def get_success_url(self):
        """Redirect to the session detail page or configuration page"""
        return reverse('session_list')
    

class LearningSessionDashboardView(LoginRequiredMixin, View):
    template_name = 'session_dashboard.html'
    
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        header, analytics,avg_task, avg_episode,total_episodes = get_session_analytics(pk)
        session = LearningSession.objects.filter(id=pk).first()
        enrollments = Enrollment.objects.filter(learning_session=session).all()
        obj = SessionRegistration.objects.filter(learning_session=session).first()
        form = RegistrationToggleForm(initial={
            'id': obj.id,
            'registration': obj.is_active
        })
        return render(request, self.template_name, 
                      {'form': form,
                        'analytics':analytics,
                        'header':header, 
                        'enrollments':len(enrollments),
                        'registration':obj,
                        'avg_task_completed':avg_task,
                        'avg_episode_completed':avg_episode,
                        'total_episodes':total_episodes})
    
    def post(self, request, *args, **kwargs):
        form = RegistrationToggleForm(request.POST)
        if form.is_valid():
            obj = SessionRegistration.objects.get(pk=form.cleaned_data['id'])
            obj.is_active = form.cleaned_data['registration']
            obj.save()
            
            status = "enabled" if form.cleaned_data['registration'] else "disabled"
            messages.success(request, f"Registration {status} successfully!")
            return redirect('session_dashboard',pk=obj.learning_session.id)


class LearningSessionListView(StaffUserRequiredMixin,LoginRequiredMixin,ListView):
    model = LearningSession
    template_name = 'session_list.html'
    context_object_name = 'learning_sessions'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return LearningSession.objects.filter(created_by=self.request.user)
        return LearningSession.objects.none()


class LearningSessionRegisterView(LoginRequiredMixin,View):

    template_name = 'session_registration.html'
    def get(self,request,code):
        try: 
            registration = SessionRegistration.objects.filter(code=code).first()

            if registration and registration.is_active:
                print(registration.learning_session,':',request.user)
                
                new_obj, created = Enrollment.objects.get_or_create(learning_session=registration.learning_session,student=request.user)
                if created:
                    return render(request,self.template_name,{'registration_open':True, 'invalid':False})
                else:
                    messages.add_message(request,messages.INFO,f'You are already enrolled in {registration.learning_session}')
                    return redirect('student_dashboard')
            else:
                return render(request,self.template_name,{'registration_open':False, 'invalid':False})
        except ValidationError:
            return render(request,self.template_name,{'invalid':True})


class LearningSessionDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningSession
    template_name = 'learningpath_confirm_delete.html'
    success_url = reverse_lazy('session_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
 

class LearningPathDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningPath
    template_name = 'learningpath_confirm_delete.html'
    success_url = reverse_lazy('learning_path_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
 
##########################################
class LearningPathConfigView(LoginRequiredMixin, View):
    template_name = 'trajectory_config_form.html'
    success_url = '/trajectory/list'
    form_class = LearningPathForm
    
    def get(self, request, pk):
        episode_form = EpisodeForm()
        learning_task_form = LearningTaskForm()
        resource_form = ResourceForm()
        learning_path_object = LearningPath.objects.filter(id=pk).first()
        return render(request, self.template_name, 
                        {
                            'object':learning_path_object,
                            'outcomes':learning_path_object.learning_outcomes.split('\n'),
                            'episode_form':episode_form,
                            'learning_task_form':learning_task_form,
                            'resource_form':resource_form
                        })


class LearningPathUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningPath
    form_class = LearningPathForm
    template_name = 'trajectory_form.html'
    success_url = '/trajectory/list'
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)
    
    def get_success_url(self):
        return reverse('learning_path_config',kwargs={'pk':self.object.id})


class LearningPathListView(ListView):
    model = LearningPath
    template_name = 'trajectory_list.html'
    context_object_name = 'learning_paths'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return LearningPath.objects.filter(owner=self.request.user)
        return LearningPath.objects.none()


# Add this class to your existing views
class LearningPathDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningPath
    template_name = 'learningpath_confirm_delete.html'
    success_url = reverse_lazy('learning_path_list')
    
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class EpisodeCreateView(LoginRequiredMixin, CreateView):
    model = Episode
    fields = ['title', 'description', 'knowbits', 'skillbits', 'sequence_number']
    template_name = 'episode_form.html'
    
    def form_valid(self, form):
        form.instance.learning_path_id = self.kwargs['learning_path_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('learning_path_detail', kwargs={'pk': self.kwargs['learning_path_id']})


class EpisodeUpdateView(LoginRequiredMixin, UpdateView):
    model = Episode
    fields = ['title', 'description', 'knowbits', 'skillbits']
    template_name = 'episode_update_form.html'
    
    def get_success_url(self):
        return reverse_lazy('learning_path_config', kwargs={'pk': self.object.learning_path.id})


class EpisodeDeleteView(LoginRequiredMixin, DeleteView):
    model = Episode
    template_name = 'episode_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('learning_path_detail', kwargs={'pk': self.object.learning_path.id})


class LearningTaskCreateView(LoginRequiredMixin, CreateView):
    model = LearningTask
    fields = ['title', 'description', 'task_type', 'location', 'approximate_time', 'difficulty_level']
    template_name = 'learningtask_form.html'
    
    def form_valid(self, form):
        form.instance.episode_id = self.kwargs['episode_id']
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('episode_detail', kwargs={'pk': self.kwargs['episode_id']})


class LearningTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = LearningTask
    fields = ['title', 'description', 'task_type', 'location', 'approximate_time', 'difficulty_level']
    template_name = 'task_update_form.html'
    
    def get_success_url(self):
        return reverse_lazy('learning_path_list')


class LearningTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningTask
    template_name = 'learningtask_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('episode_detail', kwargs={'pk': self.object.episode.id})


class ResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = Resource
    fields = ['title','h5p', 'url']
    template_name = 'resource_update_form.html'
    
    def get_success_url(self):
        return reverse_lazy('episode_detail', kwargs={'pk': self.object.episode.id})
    

