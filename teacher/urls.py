from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EpisodeCreateView, EpisodeUpdateView, EpisodeDeleteView,
    LearningTaskCreateView, LearningTaskUpdateView, LearningTaskDeleteView,
)
from .api import (
        EpisodeViewSet, 
        LearningTaskViewSet
)

from .views import (
    LearningPathCreateView, 
    LearningPathUpdateView, 
    LearningPathListView,
    LearningPathDeleteView
)

router = DefaultRouter()
router.register(r'api/episodes', EpisodeViewSet)
router.register(r'api/learningtasks', LearningTaskViewSet)

urlpatterns = [
    # Web Views
    path('learningpath/<int:learning_path_id>/episode/create/', EpisodeCreateView.as_view(), name='episode_create'),
    path('episode/<int:pk>/update/', EpisodeUpdateView.as_view(), name='episode_update'),
    path('episode/<int:pk>/delete/', EpisodeDeleteView.as_view(), name='episode_delete'),
    
    path('episode/<int:episode_id>/learningtask/create/', LearningTaskCreateView.as_view(), name='learningtask_create'),
    path('learningtask/<int:pk>/update/', LearningTaskUpdateView.as_view(), name='learningtask_update'),
    path('learningtask/<int:pk>/delete/', LearningTaskDeleteView.as_view(), name='learningtask_delete'),
    
    # API Endpoints
    path('', include(router.urls)),
]
urlpatterns = [
    path('create/', LearningPathCreateView.as_view(), name='learning_path_create'),
    path('update/<int:pk>/', LearningPathUpdateView.as_view(), name='learning_path_update'),
    path('list/', LearningPathListView.as_view(), name='learning_path_list'),
    # Add this path to your existing urlpatterns
    path('delete/<int:pk>/', LearningPathDeleteView.as_view(), name='learning_path_delete'),
    
]