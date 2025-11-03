from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
     class Meta:
          model=Project
          fields = ['id', 'owner', 'title', 'description', 'link', 'image', 'date_create']
          read_only_fields = ['id', 'owner', 'data_created']

          def create(self, validated_data):
               user = self.context['request'].user
               project = project.objects.create(owner=user, **validated_data)
               return project