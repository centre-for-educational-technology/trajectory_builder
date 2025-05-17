from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Episode, LearningTask, Resource
from .serializers import EpisodeSerializer, LearningTaskSerializer, ResourceSerializer
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
        episode = Episode.objects.filter(id=int(episode_id))
        print('Obtained:',episode_id)
        serializer.save(episode_id=episode_id)

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
        task = self.get_object()
        self.perform_destroy(task)
        return Response(
            {"detail": "Task deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(learning_task__episode__learning_path__owner=self.request.user)

    def perform_create(self, serializer):
        print('===> Called api endpoint')
        task_id = self.request.data.get('learning_task')
        print('Task:',task_id)
        serializer.save(learning_task_id=task_id)

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
        resource = self.get_object()
        self.perform_destroy(resource)
        return Response(
            {"detail": "Resource deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )