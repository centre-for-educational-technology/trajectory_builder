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

from django.conf import settings

from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from .forms import LearningPathForm, ResourceForm, EpisodeForm, LearningTaskForm, LearningSessionForm
from .models import LearningPath, Episode, LearningTask, Resource


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


class LearningSessionListView(ListView):
    model = LearningSession
    template_name = 'session_list.html'
    context_object_name = 'learning_sessions'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return LearningSession.objects.filter(created_by=self.request.user)
        return LearningSession.objects.none()
    

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
