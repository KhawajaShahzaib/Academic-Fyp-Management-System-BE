# serializers.py
from rest_framework import serializers
from .models import  Group, GroupMembership, GroupMeeting, FYPIdea
from xauth.models import Student


from rest_framework import serializers
from .models import SupervisionRequest

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Add username field
    

    class Meta:
        model = Student
        fields = ['username']  # Include the user field if it exists in the Student model

class GroupMembershipSerializer(serializers.ModelSerializer):
    student = StudentSerializer()  # Include student details in the GroupMembership serializer

    class Meta:
        model = GroupMembership
        fields = ['group', 'student']  # Adjust as needed

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        members = GroupMembershipSerializer(many=True, source='members')
        # group_members = GroupMembershipSerializer(many=True, source='group.members')  # Fetch group members #My Added
        fields = ['group_id', 'project_title', 'course', 'members']  # Add other relevant fields if needed



class SupervisionRequestSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    group_members = GroupMembershipSerializer(many=True, source='group.members')  # Include group members

    class Meta:
        model = SupervisionRequest
        fields = ['id', 'group', 'supervisor',  'description', 'status', 'group_members']


class GroupMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMeeting
        fields = ['id', 'group', 'date', 'time', 'status']

class FypIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FYPIdea
        fields = ['title', 'description', 'domain', 'preferred_degree', 'supervisor']
         
    def validate(self, attrs):
        print(attrs)  # Log incoming data to see what is being received
        return super().validate(attrs)
    

#Director
from .models import Course, Faculty, FypManager

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

from xauth.serializers import DepartmentSerializer, UserSerializer
from xauth.models import User
class FacultySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    user = UserSerializer() 

    class Meta:
        model = Faculty
        username = serializers.CharField(source='user.username', read_only=True)
        fields = ['user', 'faculty_id', 'faculty_code', 'is_director', 'is_hod', 'department', 'user']

class FypManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FypManager
        fields = '__all__'

from .models import Submission, Presentation, CLO, Assessment, AssessmentCriteria, Timetable, TimetableEntry
class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['title', 'description', 'course', 'deadline', 'file'] 

class PresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presentation
        fields = '__all__'

class CLOSerializer(serializers.ModelSerializer):
    class Meta:
        model = CLO
        fields = ['clo_id', 'title', 'clo_number']

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'  # or specify fields as a list

class AssessmentCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentCriteria
        fields = ['assessment', 'criteria', 'max_score', 'clo_link', 'criteria_id']

    def validate(self, data):
        # Example validation logic
        if not data.get('assessment'):
            raise serializers.ValidationError({"assessment": "This field is required."})
        if not data.get('criteria'):
            raise serializers.ValidationError({"criteria": "This field is required."})
        if not data.get('max_score'):
            raise serializers.ValidationError({"max_score": "This field is required."})
        if not data.get('clo_link'):
            raise serializers.ValidationError({"clo_link": "This field is required."})
        return data
   
class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ['course', 'file']

class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = ['teacher', 'room', 'day', 'time']

