from django.urls import path
from .views import StudentDashboardView, LearningPathDetailView, TaskView, StudentProfileUpdateView, StudentProfileDetailView


urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/update/', StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('profile/', StudentProfileDetailView.as_view(), name='student_profile'),
    path('task/',TaskView.as_view(),name='task'),
    path('learning-path/<int:path_id>/<int:episode_index>/<int:task_index>/', LearningPathDetailView.as_view(), name='learning_path'),
    path('learning-path/<int:path_id>/', LearningPathDetailView.as_view(), name='learning_path_start'),
]
