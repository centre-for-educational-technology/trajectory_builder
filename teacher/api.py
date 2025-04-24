from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Episode, LearningTask
from .serializers import EpisodeSerializer, LearningTaskSerializer

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(learning_path__owner=self.request.user)

    def perform_create(self, serializer):
        learning_path_id = self.request.data.get('learning_path')
        serializer.save(learning_path_id=learning_path_id)

class LearningTaskViewSet(viewsets.ModelViewSet):
    queryset = LearningTask.objects.all()
    serializer_class = LearningTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(episode__learning_path__owner=self.request.user)

    def perform_create(self, serializer):
        episode_id = self.request.data.get('episode')
        serializer.save(episode_id=episode_id)