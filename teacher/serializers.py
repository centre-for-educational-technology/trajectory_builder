from rest_framework import serializers
from .models import Episode, LearningTask, Resource

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'

class LearningTaskSerializer(serializers.ModelSerializer):
    resources = ResourceSerializer(many=True, read_only=True)
    class Meta:
        model = LearningTask
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class EpisodeSerializer(serializers.ModelSerializer):
    learning_tasks = LearningTaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Episode
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'sequence_number')

