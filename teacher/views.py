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
from .models import Episode, LearningTask, Resource


from django.urls import reverse
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.views.generic.edit import FormView
from .forms import LearningPathForm, ResourceForm, EpisodeForm, LearningTaskForm
from .models import LearningPath, Episode, LearningTask, Resource


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
    fields = ['title', 'description', 'knowbits', 'skillbits', 'sequence_number']
    template_name = 'episode_form.html'
    
    def get_success_url(self):
        return reverse_lazy('learning_path_detail', kwargs={'pk': self.object.learning_path.id})

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
    template_name = 'learningtask_form.html'
    
    def get_success_url(self):
        return reverse_lazy('episode_detail', kwargs={'pk': self.object.episode.id})

class LearningTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = LearningTask
    template_name = 'learningtask_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('episode_detail', kwargs={'pk': self.object.episode.id})