from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EpisodeCreateView, EpisodeUpdateView, EpisodeDeleteView,
    LearningTaskCreateView, LearningTaskUpdateView, LearningTaskDeleteView,
    LearningPathConfigView, ResourceUpdateView, LearningSessionCreateView, LearningSessionUpdateView,
    LearningSessionDeleteView, LearningSessionListView
)
from .api import (
        EpisodeViewSet, 
        LearningTaskViewSet,
        ResourceViewSet
)

from .views import (
    LearningPathCreateView, 
    LearningPathUpdateView, 
    LearningPathListView,
    LearningPathDeleteView,
    H5PProxySearchView
)

router = DefaultRouter()
router.register(r'episodes', EpisodeViewSet)
router.register(r'learningtasks', LearningTaskViewSet)
router.register(r'resources', ResourceViewSet)

urlpatterns = [
    # Web Views
    path('learningpath/<int:learning_path_id>/episode/create/', EpisodeCreateView.as_view(), name='episode_create'),
    path('episode/<int:pk>/update/', EpisodeUpdateView.as_view(), name='episode_update'),
    path('episode/<int:pk>/delete/', EpisodeDeleteView.as_view(), name='episode_delete'),
    
    path('episode/<int:episode_id>/learningtask/create/', LearningTaskCreateView.as_view(), name='learningtask_create'),
    path('learningtask/<int:pk>/update/', LearningTaskUpdateView.as_view(), name='learningtask_update'),
    path('learningtask/<int:pk>/delete/', LearningTaskDeleteView.as_view(), name='learningtask_delete'),

]
urlpatterns = [
    path('create/', LearningPathCreateView.as_view(), name='learning_path_create'),
    path('update/<int:pk>/', LearningPathUpdateView.as_view(), name='learning_path_update'),
    path('list/', LearningPathListView.as_view(), name='learning_path_list'),
    path('configure/<int:pk>/', LearningPathConfigView.as_view(), name='learning_path_config'),
    path('delete/<int:pk>/', LearningPathDeleteView.as_view(), name='learning_path_delete'),

    # Learning Session urls
    path('session/create/', LearningSessionCreateView.as_view(), name='session_create'),
    path('session/update/<int:pk>/', LearningSessionUpdateView.as_view(), name='session_update'),
    path('session/list/', LearningSessionListView.as_view(), name='session_list'),
    path('session/delete/<int:pk>/', LearningSessionDeleteView.as_view(), name='session_delete'),

    # API endpoints
    path('', include(router.urls)),

    # Update urls for resource, task and episode
    path('resource/<int:pk>/update/', ResourceUpdateView.as_view(), name='resource_update'),
    path('learningtask/<int:pk>/update/', LearningTaskUpdateView.as_view(), name='learningtask_update'),
    path('episode/<int:pk>/update/', EpisodeUpdateView.as_view(), name='episode_update'),

    # Vara h5p elements
    path('vara/h5p-search', H5PProxySearchView.as_view(), name='h5p_proxy_search'),
    
]