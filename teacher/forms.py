from django import forms
from .models import LearningPath

class LearningPathForm(forms.ModelForm):
    class Meta:
        model = LearningPath
        fields = [
            'title', 
            'description', 
            'school_level', 
            'subject', 
            'topics', 
            'sub_topics', 
            'learning_outcomes'
        ]
        help_texts = {'title':'', 
            'description':'Brief overview of the trajectory, highlighting key milestones and a path forward.', 
            'school_level':'', 
            'subject':'', 
            'topics':'', 
            'sub_topics':'', 
            'learning_outcomes':''}
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'learning_outcomes': forms.Textarea(attrs={'rows': 4}),
            'school_level': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and hasattr(self.request, 'user'):
            instance.owner = self.request.user
        if commit:
            instance.save()
        return instance


        from django import forms
from .models import Episode, LearningTask

class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ['title', 'description', 'knowbits', 'skillbits', 'sequence_number']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter episode title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Describe this episode'
            }),
            'knowbits': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'skillbits': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'sequence_number': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'min': 1
            })
        }
        labels = {
            'knowbits': 'Knowledge Components',
            'skillbits': 'Skill Components'
        }

    def __init__(self, *args, **kwargs):
        learning_path = kwargs.pop('learning_path', None)
        super().__init__(*args, **kwargs)
        if learning_path:
            last_episode = Episode.objects.filter(learning_path=learning_path).order_by('-sequence_number').first()
            self.fields['sequence_number'].initial = (last_episode.sequence_number + 1) if last_episode else 1

class LearningTaskForm(forms.ModelForm):
    class Meta:
        model = LearningTask
        fields = ['title', 'description', 'task_type', 'location', 'approximate_time', 'difficulty_level']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 3,
                'placeholder': 'Describe this task'
            }),
            'task_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Classroom, Lab, etc.'
            }),
            'approximate_time': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'type': 'text',
                'placeholder': 'HH:MM:SS or 1h 30m'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500'
            })
        }
        help_texts = {
            'approximate_time': 'Enter duration in hours:minutes:seconds format (e.g., 1:30:00 for 1 hour 30 minutes)'
        }

    def clean_approximate_time(self):
        time_str = self.cleaned_data['approximate_time']
        try:
            # Handle different time input formats
            if ':' in time_str:
                h, m, s = map(int, time_str.split(':'))
                return timedelta(hours=h, minutes=m, seconds=s)
            elif 'h' in time_str.lower():
                parts = time_str.lower().split('h')
                hours = int(parts[0])
                minutes = int(parts[1].split('m')[0]) if 'm' in parts[1] else 0
                return timedelta(hours=hours, minutes=minutes)
            return timedelta(minutes=int(time_str))
        except (ValueError, AttributeError):
            raise forms.ValidationError("Enter time in HH:MM:SS or '1h 30m' format")