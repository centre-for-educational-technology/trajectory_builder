from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Episode, LearningTask
from .serializers import EpisodeSerializer, LearningTaskSerializer
from rest_framework.response import Response
from rest_framework import status

class EpisodeViewSet(viewsets.ModelViewSet):
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(learning_path__owner=self.request.user)

    def perform_create(self, serializer):
        learning_path_id = self.request.data.get('learning_path')
        serializer.save(learning_path_id=learning_path_id)

    def perform_destroy(self, instance):
        # <-- called by the default destroy()
        # you could do extra cleanup/logging here:
        # log_deletion(user=self.request.user, episode=instance)
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy if you need a custom response or additional checks.
        By default, ModelViewSet.destroy() calls perform_destroy() then
        returns HTTP 204.
        """
        episode = self.get_object()
        self.perform_destroy(episode)
        return Response(
            {"detail": "Episode deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class LearningTaskViewSet(viewsets.ModelViewSet):
    queryset = LearningTask.objects.all()
    serializer_class = LearningTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(episode__learning_path__owner=self.request.user)

    def perform_create(self, serializer):
        episode_id = self.request.data.get('episode')
        serializer.save(episode_id=episode_id)