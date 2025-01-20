# serializers.py
from rest_framework import serializers
from .models import  Group, GroupMembership, GroupMeeting, FYPIdea
from xauth.models import Student


from rest_framework import serializers
from .models import SupervisionRequest, Semester, Supervisor, Room
from xauth.serializers import DegreeSerializer

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Add username field

    class Meta:
        model = Student
        fields = ['sap_id', 'username']


class SupervisorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Add username field

    class Meta:
        model = Supervisor
        fields = ['username']

class GroupMembershipSerializer(serializers.ModelSerializer):
    student = StudentSerializer()  # Include student details in the GroupMembership serializer

    class Meta:
        model = GroupMembership
        fields = ['group', 'student']  # Adjust as needed

class GroupSerializer(serializers.ModelSerializer):
    members = GroupMembershipSerializer(many=True, source='membership')
    supervisor = SupervisorSerializer()
    class Meta:
        model = Group
        fields = ['group_id', 'project_title', 'supervisor', 'course', 'members']  # Add other relevant fields if needed



class SupervisionRequestSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    # group_members = GroupMembershipSerializer(many=True, source='group.membership')  # Include group members

    class Meta:
        model = SupervisionRequest
        fields = ['id', 'group', 'supervisor',  'description', 'status']

class GroupMeetingOldSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMeeting
        fields = ['id', 'group', 'date', 'time', 'status']

class GroupMeetingSerializer(serializers.ModelSerializer):
    group = GroupSerializer() 
    class Meta:
        model = GroupMeeting
        fields = ['id', 'group', 'date', 'time', 'status']
from .models import Attendance
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'meeting', 'assessment', 'is_present']  # Include fields you want to expose
        read_only_fields = ['id', 'meeting', 'assessment']

    def update(self, instance, validated_data):
        # Update the attendance record when marking as present or absent
        instance.is_present = validated_data.get('is_present', instance.is_present)
        instance.save()
        return instance

class FypIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FYPIdea
        fields = ['title', 'description', 'domain', 'preferred_degree', 'supervisor']
         
    def validate(self, attrs):
        print(attrs)  # Log incoming data to see what is being received
        return super().validate(attrs)
    
class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['semester_id', 'semester_name', 'start_date', 'end_date']
#Director
from .models import Course, Faculty, FypManager

class CourseSerializer(serializers.ModelSerializer):
    degree = DegreeSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'  # Include all model fields
        # fields += ('degree_name', 'semester_name')  # Add custom fields

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
    scheduled_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", input_formats=["%Y-%m-%dT%H:%M"])
    panel_members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Faculty.objects.all()
    )
    class Meta:
        model = Presentation
        fields = ['scheduled_time', 'assessment', 'course', 'student_group', 'room_no', 'panel_members'] 


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

class PresentationSerializerViewer(serializers.ModelSerializer):
    scheduled_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", input_formats=["%Y-%m-%dT%H:%M"])
    panel_members = FacultySerializer(many=True)  # Nested serializer for panel members
    course = CourseSerializer()  # Nested serializer for course
    student_group = GroupSerializer()  # Nested serializer for student group
    assessment = AssessmentSerializer()  # Nested serializer for assessment

    class Meta:
        model = Presentation
        fields = ['scheduled_time', 'assessment', 'course', 'student_group', 'room_no', 'panel_members', 'id', 'feedback']