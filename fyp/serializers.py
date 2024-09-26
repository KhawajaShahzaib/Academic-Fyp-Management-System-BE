# serializers.py
from rest_framework import serializers
from .models import FYPIdea, Meeting, StudentGroup, Specialty, Request, ProjectGroup

class FYPIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FYPIdea
        fields = '__all__'  # Or specify fields explicitly

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = '__all__'

class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
