from django.urls import path
from .views import StudentDashboardView, LearningPathStudentView, TaskView, StudentProfileUpdateView, StudentProfileDetailView


urlpatterns = [
    path('dashboard/', StudentDashboardView.as_view(), name='dashboard'),
    path('profile/update/', StudentProfileUpdateView.as_view(), name='student_profile_update'),
    path('profile/', StudentProfileDetailView.as_view(), name='student_profile'),
    path('learning-path/<int:session_id>/', LearningPathStudentView.as_view(), name='learning_path'),
    path('learning-path/<int:session_id>/task/<int:task_id>', TaskView.as_view(), name='learning_path_task'),
]
