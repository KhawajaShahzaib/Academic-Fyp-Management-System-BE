from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
# from .models import FYPIdea, Meeting, Specialty, Request
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import FacultyDepartmentRole, Faculty, Role
from .models import Supervisor, Speciality, SupervisionRequest, Group, GroupMeeting, FYPIdea
from .models import Assessment, AssessmentCriteria,  TimetableEntry, CLO

from rest_framework.views import APIView

from .serializers import SupervisionRequestSerializer, GroupMeetingSerializer, GroupSerializer, FypIdeaSerializer
from .serializers import SubmissionSerializer, AssessmentSerializer, AssessmentCriteriaSerializer, CLOSerializer, TimetableSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.utils.timezone import now
from .models import Room
from .serializers import RoomSerializer

class RoomListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rooms = Room.objects.all().order_by('name')  # Sorts rooms alphabetically by name
        print("rooms: ", rooms)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    def post(self, request):

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            room.delete()
            return Response({"message": "Room deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_and_assign_supervisor_role(request): 
    user = request.user

    if user.user_type == 'faculty':
        faculty = get_object_or_404(Faculty, user=user)
        
        # Get all roles assigned to the faculty member
        role_assignments = FacultyDepartmentRole.objects.filter(faculty=faculty)
        roles = [assignment.role.role_name for assignment in role_assignments]
        
        # If no roles, assign Supervisor role by default
        if not roles:
            supervisor_role, created = Role.objects.get_or_create(role_name="Supervisor")
            
            department = faculty.department
            FacultyDepartmentRole.objects.create(faculty=faculty, department=department, role=supervisor_role)
            Supervisor.objects.create(user=faculty)
            roles = ['Supervisor']
        
        
        return JsonResponse({"roles": roles}, status=200)
    print("User: ", user.user_type)
    if user.user_type == 'student':
        roles = ['Student']
        return JsonResponse({"roles": roles}, status=200)


    return JsonResponse({"message": "User is not a faculty member."}, status=403)


import json
@api_view(['POST'])  # Assuming this will be called after login
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def update_supervisor_specialties(request):
    if request.method == 'POST':
        user = request.user
        if user.user_type == 'faculty':
            faculty = get_object_or_404(Faculty, user=user)
            supervisor = get_object_or_404(Supervisor, user=faculty)

            # Get the specialties from the request body
            data = json.loads(request.body)
            specialty_names = data.get('specialties', [])
            if len(specialty_names) > 3:
                return JsonResponse({"message": "You cannot add more than 3 specialties."}, status=400)

            # Update the supervisor's specialties
            for s in specialty_names:
                supervisor_role, created = Speciality.objects.get_or_create(name=s)
            specialties = Speciality.objects.filter(name__in=specialty_names)
            supervisor.specialities.set(specialties)
            supervisor.save()

            return JsonResponse({"message": "Specialties updated successfully."}, status=200)

        return JsonResponse({"message": "User is not a faculty member."}, status=403)

    return JsonResponse({"message": "Invalid request method."}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def get_supervision_requests(request):
    try:
        user = request.user
        # Fetch supervisor object for the current logged-in user
        faculty = get_object_or_404(Faculty, user=user)
        supervisor = Supervisor.objects.get(user=faculty)
        
        # Get all pending supervision requests for the supervisor
        supervision_requests = SupervisionRequest.objects.filter(supervisor=supervisor, status='pending')
        serializer = SupervisionRequestSerializer(supervision_requests, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Supervisor.DoesNotExist:
        return JsonResponse({'detail': 'Supervisor not found'}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated]) 
class SupervisionRequestViewSet(viewsets.ModelViewSet):
    def list(self, request):
        # supervisor = request.user  # Assuming that the user is a Faculty and has a related supervisor model
        faculty = get_object_or_404(Faculty, user=request.user)
        supervisor = get_object_or_404(Supervisor, user=faculty)
        print("Supervisor is: ", supervisor.user.user.username)
        # Filter requests that are pending and made for this supervisor
        queryset = SupervisionRequest.objects.filter(supervisor=supervisor, status='pending')
        # queryset = SupervisionRequest.objects.all()
        serializer = SupervisionRequestSerializer(queryset, many=True)
        print("serializers Data Complete: ", serializer.data)
        return Response(serializer.data)
    # permission_classes = IsAuthenticated

    def update(self, request, pk=None):
        try:
            supervision_request = SupervisionRequest.objects.get(pk=pk)
            action = request.data.get('action')

            if action == 'accept':
                supervision_request.status = 'accepted'
                group = supervision_request.group  # Assuming supervision_request has a related group
                faculty = get_object_or_404(Faculty, user=request.user)
                # supervisor = get_object_or_404(Supervisor, user=faculty)
                group.supervisor = faculty  # Set the supervisor from the request
                group.save() 
                
            elif action == 'reject':
                supervision_request.status = 'rejected'
                print("About to delete supervision request with Group:", supervision_request)
                # supervision_request.delete()
                # supervision_request.save()
                
            else:
                return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

            supervision_request.save()
            serializer = SupervisionRequestSerializer(supervision_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SupervisionRequest.DoesNotExist:
            return Response({"detail": "Supervision request not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def respond_to_supervision_request(request, request_id):
    try:
        supervision_request = SupervisionRequest.objects.get(id=request_id)
    except SupervisionRequest.DoesNotExist:
        return JsonResponse({"message": "Request not found."}, status=404)

    action = request.data.get('action')

    if action == 'accept':
        supervision_request.status = 'accepted'
        supervision_request.group.supervisor = supervision_request.supervisor.user
        supervision_request.group.save()
    elif action == 'reject':
        supervision_request.status = 'rejected'
    else:
        return JsonResponse({"message": "Invalid action."}, status=400)

    supervision_request.save()
    return JsonResponse({"message": "Request updated successfully."}, status=200)


from .serializers import GroupMeetingOldSerializer
class MeetingViewSet(viewsets.ModelViewSet):
    queryset = GroupMeeting.objects.all()
    serializer_class = GroupMeetingSerializer
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get_queryset(self):
        user = self.request.user
        faculty = get_object_or_404(Faculty, user=user)
        
        # Get all groups supervised by this faculty
        groups = Group.objects.filter(supervisor=faculty)

        # Return all meetings for those groups
        return GroupMeeting.objects.filter(group__in=groups)

    def create(self, request, *args, **kwargs):
        serializer = GroupMeetingOldSerializer(data=request.data)
        print("Serializer data received: ", request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get_queryset(self):
        # Get the supervisor from the request user
        user = self.request.user  # Assuming the user is a Supervisor
        faculty = get_object_or_404(Faculty, user=user)
        # supervisor = get_object_or_404(Supervisor, user=faculty)
        print("Group Result: ", Group.objects.filter(supervisor=faculty))

        return Group.objects.filter(supervisor=faculty)
    

class FypIdeaViewSet(viewsets.ModelViewSet):
    serializer_class = FypIdeaSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    queryset = FYPIdea.objects.all()

    def get_queryset(self):
        # Optionally filter by the logged-in user
        return FYPIdea.objects.filter(supervisor__user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically set the supervisor based on the requesting user
        user = self.request.user
    
        faculty = get_object_or_404(Faculty,user=user)
        # Assuming you have a way to retrieve the supervisor based on the user
        supervisor = get_object_or_404(Supervisor, user=faculty)
        serializer.save(supervisor=supervisor)
        serializer.save()
        print("Serializer: ", serializer)


#Director 
from xauth.serializers import FacultySerializer
from .models import Course, Faculty, FypManager
from .serializers import CourseSerializer, FacultySerializer, FypManagerSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses(request):
    user = request.user
    if user.user_type == 'student':
        try:
            student = Student(user=user)
            print('student accessed', student)
        except:
            return serializer.data()
    faculty = get_object_or_404(Faculty, user=user)
    fyp_manager = FypManager.objects.filter(user=faculty).first()
    
    if fyp_manager:
        # Filter courses that are assigned to this FypManager
        assigned_courses = fyp_manager.course.all()
    else:
        assigned_courses = []
    
    # Serialize the assigned courses
    serializer = CourseSerializer(assigned_courses, many=True)
    return Response(serializer.data)
class FacultyViewSet(viewsets.ModelViewSet):  # Change here
    permission_classes = [IsAuthenticated]  
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer

class FypManagerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  
    queryset = FypManager.objects.all()
    serializer_class = FypManagerSerializer

    def create(self, request, *args, **kwargs):

        faculty_id = request.data.get('user')  # This should be the faculty_id from the request
        course_ids = request.data.get('course', [])  # Fetch the course IDs from request data

        try:
            faculty = Faculty.objects.get(faculty_id=faculty_id)
        except Faculty.DoesNotExist:
            return Response({"error": "Faculty not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the FypManager instance first
        fyp_manager = FypManager.objects.create(user=faculty)

        # Associate the courses with the FypManager
        for course_id in course_ids:
            try:
                course = Course.objects.get(course_id=course_id)
                fyp_manager.course.add(course)  # Add course to FypManager
            except Course.DoesNotExist:
                return Response({"error": f"Course with ID {course_id} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(fyp_manager)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


########################
#Abdullah
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_submission(request):
    print("Received data: ", request.data)  
    serializer = SubmissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Errors: ", serializer.errors)  # Log validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_clos(request):
    course_id = request.query_params.get('course_id')
    if course_id:
        clos = CLO.objects.filter(course_id=course_id)  
    # user=request.user
    # print("User Accessing is:", user.username)
    else:
        clos = CLO.objects.all()
    serializer = CLOSerializer(clos, many=True)
    # print("serializer sending data: ", serializer.data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assessment(request):
    serializer = AssessmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assessments(request):
    print("data: ", request.data)
    course_id = request.query_params.get('course_id')  # Get the course ID from query parameters
    if course_id:
        assessments = Assessment.objects.filter(course_id=course_id)  # Filter by course
    else:
        assessments = Assessment.objects.all()  # Return all assessments if no course ID is provided

    serializer = AssessmentSerializer(assessments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assessment_with_criteria(request):
    print("Data received: ", request.data)
    # Create assessment
    # Create criteria for the assessment
    criteria_list = request.data.get('criteria', [])
    assessment_id = request.data.get('assessmentid')
    
    for question in criteria_list:
        criteria_data = {
            'assessment': assessment_id,  # Use the ID of the saved assessment
            'criteria': question.get('criteria'),
            'max_score': question.get('max_score'),
            'clo_link': question.get('clo_link'),  # Pass ID of the CLO
        }
        
        # Check if this criteria already exists
        if AssessmentCriteria.objects.filter(assessment=assessment_id, criteria=question.get('criteria')).exists():
            print(f"Duplicate question found: {question.get('criteria')}, skipping.")
            continue  # Skip saving the duplicate
        
        criteria_serializer = AssessmentCriteriaSerializer(data=criteria_data)
        if criteria_serializer.is_valid():
            criteria_serializer.save()
        else:
            # Return error if any criteria is invalid
            print("Invalid data:", criteria_serializer.errors)
            return Response(criteria_serializer.errors, status=400)
    
    return Response({"message": "Assessment criteria created successfully"}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_question(request, question_id):
    try:
        question = AssessmentCriteria.objects.get(id=question_id)
        question.delete()
        return Response({"message": "Question removed successfully."}, status=status.HTTP_200_OK)
    except AssessmentCriteria.DoesNotExist:
        return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_question(request, question_id):
    try:
        question = AssessmentCriteria.objects.get(id=question_id)
        data = request.data
        question.criteria = data.get('criteria', question.criteria)
        question.max_score = data.get('max_score', question.max_score)
        question.clo_link_id = data.get('clo_link', question.clo_link_id)
        question.save()
        return Response({"message": "Question updated successfully."}, status=status.HTTP_200_OK)
    except AssessmentCriteria.DoesNotExist:
        return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_timetable(request):
    print("Received data: ", request.data)  
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Errors: ", serializer.errors)  # Log validation errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# import openpyxl
from rest_framework.views import APIView

# class TimetableUploadView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Check if a file was uploaded
#         file = request.FILES.get('file')
#         if not file:
#             return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Load the uploaded file
#             workbook = openpyxl.load_workbook(file)
#             sheet = workbook.active

#             # Process the file data
#             timetable_data = []
#             for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
#                 teacher_name = row[0]
#                 day = row[1]
#                 time = row[2]

#                 # Store data in the database if needed or prepare it for response
#                 timetable_data.append({
#                     "teacher_name": teacher_name,
#                     "day": day,
#                     "time": time
#                 })

#             return Response({"message": "File processed successfully", "data": timetable_data}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from tablib import Dataset
from .resources import TimetableEntryResource
def simple_upload(request):
    if request.method == 'POST':
        timetable_resource = TimetableEntryResource()
        dataset = Dataset()
        uploaded_file = request.FILES.get('myfile')

        # Check if file format is valid
        if not uploaded_file.name.endswith('xlsx'):
            return JsonResponse({'error': 'Wrong file format. Please upload an .xlsx file.'}, status=400)

        try:
            # Load data from the uploaded file
            imported_data = dataset.load(uploaded_file.read(), format='xlsx')

            # Iterate through each entry and save it to the database
            for data in imported_data:
                value = TimetableEntry(
                    teacher=data[0],
                    room=data[1],
                    day=data[2],
                    time=data[3],
                )
                value.save()

            return JsonResponse({'success': 'File uploaded and data imported successfully.'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

from rest_framework.parsers import MultiPartParser, FormParser

class TimetableUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = TimetableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "File uploaded successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from .models import Timetable, Timetable_json
from rest_framework.views import APIView

class TimetableJsonUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')  # Get the uploaded file
        
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file)

            # Convert the DataFrame to JSON
            json_data = df.to_json(orient='records')
            print("Json data: ", json_data)

            # Save the JSON data to the database
            timetable = Timetable_json(data=json_data)  # Assuming 'data' is a JSONField in your model
            timetable.save()

            return Response({"message": "File uploaded and data saved as JSON successfully!"}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

#My View:
from django.core.files.base import ContentFile
import pandas as pd


#Assessments management
class AssessmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Retrieve all assessments or filter by course ID."""
        course_id = request.query_params.get('course_id')
        if course_id:
            assessments = Assessment.objects.filter(course_id=course_id)
        else:
            assessments = Assessment.objects.all()
        
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Create a new assessment."""
        serializer = AssessmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user.faculty)  # Assuming `request.user` is linked to Faculty
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, *args, **kwargs):
        """Update an existing assessment."""
        assessment = get_object_or_404(Assessment, pk=pk)
        serializer = AssessmentSerializer(assessment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        """Delete an existing assessment."""
        assessment = get_object_or_404(Assessment, pk=pk)
        assessment.delete()
        return Response({"message": "Assessment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from django.views import View
class AssessmentQuestionsView(View):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, assessment_id, *args, **kwargs):
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
            questions = AssessmentCriteria.objects.filter(assessment=assessment)
            questions_data = AssessmentCriteriaSerializer(questions, many=True).data
            print("questions data: ", questions_data)
            
            return JsonResponse({
                "assessment_name": assessment.name,
                "questions": questions_data
            }, status=200)
        except Assessment.DoesNotExist:
            return JsonResponse({"error": "Assessment not found"}, status=404)
    
    def post(self, request, *args, **kwargs):
        data = request.data
        print("Data received: ", data)

        criteria_list = data.get('criteria', [])
        assessment_id = data.get('assessmentid')

        for question in criteria_list:
            criteria_data = {
                'assessment': assessment_id,
                'criteria': question.get('criteria'),
                'max_score': question.get('max_score'),
                'clo_link': question.get('clo_link'),
            }
            criteria_serializer = AssessmentCriteriaSerializer(data=criteria_data)
            
            if criteria_serializer.is_valid():
                criteria_serializer.save()
            else:
                print("Invalid data:", criteria_serializer.errors)
                return JsonResponse(criteria_serializer.errors, status=400)
        
        return JsonResponse({"message": "Assessment criteria created successfully"}, status=200)



class AssessmentCriteriaDetailView(APIView):
    def put(self, request, question_id):
        """Handle full update of a record"""
        try:
            criteria = AssessmentCriteria.objects.get(pk=question_id)
            serializer = AssessmentCriteriaSerializer(criteria, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AssessmentCriteria.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, question_id):
        """Handle partial update of a record"""
        try:
            criteria = AssessmentCriteria.objects.get(pk=question_id)
            serializer = AssessmentCriteriaSerializer(criteria, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AssessmentCriteria.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, question_id):
        """Handle deletion of a record"""
        try:
            criteria = AssessmentCriteria.objects.get(pk=question_id)
            criteria.delete()
            return Response({"message": "Question deleted successfully."}, status=status.HTTP_200_OK)
        except AssessmentCriteria.DoesNotExist:
            return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from datetime import datetime

from .serializers import PresentationSerializer, PresentationSerializerViewer
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ObjectDoesNotExist
from xauth.models import User

class UserSchedulePresentationView(APIView):
    def get(self, request):
        try:
            current_user = request.user
            print("requesting user: ", current_user)
            faculty = Faculty.objects.filter(user=current_user)
            presentations = Presentation.objects.filter(panel_members__in=faculty)
            print("presentation he have: ", presentations)
            serializer = PresentationSerializerViewer(presentations, many=True)
            # print("Serializer sending data: ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:

            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]  
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def get_fyp_groups_all(self, request, course_id=None):
        course = Course.objects.get(course_id=course_id)
        projects = Group.objects.filter(course=course)
        # print("Projects: ", projects)
        serializer = GroupSerializer(projects, many=True)
        print("Serializer returning data: ", serializer.data)
        return Response(serializer.data)
    def get_fyp_groups(self, request, course_id, assessment_id):
        course = Course.objects.get(course_id=course_id)
        # Filter groups for the course
        groups = Group.objects.filter(course=course)
        # Exclude groups that already have a presentation for the given assessment
        groups_without_presentation = groups.exclude(
        presentation__assessment_id=assessment_id
        )
        # Serialize the filtered groups
        serializer = GroupSerializer(groups_without_presentation, many=True)
        return Response(serializer.data)
from datetime import timedelta

class SchedulePresentationView(APIView):
    def get(self, request, course_id, assessment_id):
        try:
            presentations = Presentation.objects.filter(course_id=course_id, assessment_id=assessment_id)
            serializer = PresentationSerializerViewer(presentations, many=True)
            # print("Serializer sending data: ", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    # def put(self, request, presentation_id):
    #     try:
    #         presentation = Presentation.objects.get(id=presentation_id)
    #         data = request.data
    #         print("presentation id: ", presentation_id)
            
    #         presentation.scheduled_time = data.get("scheduled_time", presentation.scheduled_time)
    #         presentation.room_no = data.get("room_no", presentation.room_no)
    #         print("data received: ", data)
    #         # Update panel_members if present in request data
    #         if "panel_members" in data:
    #             new_panel_members = data["panel_members"]
    #             # final_panel_members = Faculty.objects.filter(user__in=new_panel_members)
    #             print("Panel exists", " they are: ", new_panel_members)
    #             new_panel_members = Faculty.objects.filter(user__username__in=new_panel_members)
    #             presentation.panel_members.set(new_panel_members)  # Set new panel members
    #         presentation.save()
            
    #         serializer = PresentationSerializerViewer(presentation)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
        
    #     except Presentation.DoesNotExist:
    #         return Response({"error": "Presentation not found"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, presentation_id):
        try:
            presentation = Presentation.objects.get(id=presentation_id)
            data = request.data
            print("presentation id: ", presentation_id)
            
            presentation.scheduled_time = data.get("scheduled_time", presentation.scheduled_time)
            presentation.room_no = data.get("room_no", presentation.room_no)
            print("data received: ", data)
            # Update panel_members if present in request data
            if "panel_members" in data:
                new_panel_members = data["panel_members"]
                # final_panel_members = Faculty.objects.filter(user__in=new_panel_members)
                print("Panel exists", " they are: ", new_panel_members)
                new_panel_members = Faculty.objects.filter(faculty_id__in=new_panel_members)
                presentation.panel_members.set(new_panel_members)  # Set new panel members
            presentation.save()
            
            serializer = PresentationSerializerViewer(presentation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Presentation.DoesNotExist:
            return Response({"error": "Presentation not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    # def post(self, request):
    #     scheduled_time = datetime.fromisoformat(request.data['scheduled_time'])
    #     request.data['scheduled_time'] = scheduled_time
    #     print("SCHEDULE RECEIVED: ", request.data)
    #     serializer = PresentationSerializer(data=request.data)
    #     print('serializer data: ', request.data)
    #     if serializer.is_valid():
    #         print("serializer is valid")
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #Individual schedule date
    # def post(self, request):
    #     try:
    #         print("Complete data received: ", request.data)
    #         complete_data = request.data
    #         course_id = complete_data["course"]
    #         assessment_id = complete_data['assessment']
    #         data = complete_data['group']
    #         print("Group data: ", data)
    #         data_list = data  # Expecting a list of objects
    #         response_data = []  # Collect responses for each entry

    #         for data in data_list:
    #             print("first group: ", data)
    #             # Extract fields from the data
    #             scheduled_time = parse_datetime(data.get("scheduled_time"))
    #             # course_id = data.get("course")
    #             group_id = data.get("group_id")
    #             room_no = data.get("room_no")
    #             panel_member_ids = data.get("panel_members", [])

    #             # Validate required fields
    #             if not all([scheduled_time, course_id, group_id, room_no]):
    #                 response_data.append({"error": "Missing required fields", "group_id": group_id})
    #                 continue

    #             # Fetch related objects
    #             try:
    #                 course = Course.objects.get(pk=course_id)
    #                 assessment = Assessment.objects.get(pk=assessment_id)
    #                 student_group = Group.objects.get(pk=group_id)

    #                 # Create or update the Presentation instance
    #                 presentation = Presentation.objects.create(
    #                     scheduled_time=scheduled_time,
    #                     course=course,
    #                     assessment=assessment,
    #                     student_group=student_group,
    #                     room_no=room_no
    #                 )

    #                 # Link panel members (if any)
    #                 if panel_member_ids:
    #                     print("faculty id exists: ", panel_member_ids)
    #                     users = User.objects.filter(id__in=panel_member_ids)
    #                     # print("Users fetched: ", users)
    #                     panel_members = Faculty.objects.filter(faculty_id__in=panel_member_ids)
    #                     print("Panel members len: ", len(panel_members))
    #                     presentation.panel_members.set(panel_members)
    #                     print("Final presentation: ", presentation)

    #                 # Save the presentation
    #                 presentation.save()

    #                 response_data.append({"message": "Presentation submitted successfully", "group_id": group_id, "id": presentation.id})
    #             except ObjectDoesNotExist as e:
    #                 response_data.append({"error": str(e), "group_id": group_id})
    #             except Exception as e:
    #                 response_data.append({"error": str(e), "group_id": group_id})

    #         return JsonResponse(response_data, safe=False, status=207)  # 207 Multi-Status for partial success

    #     except Exception as e:
    #         return JsonResponse({"error": str(e)}, status=500)
    
    #     return JsonResponse({"error": "Invalid HTTP method"}, status=405)
    def post(self, request):
        try:
            print("Complete data received: ", request.data)
            complete_data = request.data
            course_id = complete_data["course"]
            assessment_id = complete_data['assessment']
            data = complete_data['group']
            scheduled_time = parse_datetime(complete_data.get("scheduled_time"))

            print("Group data: ", data)
            data_list = data  # Expecting a list of objects
            response_data = []  # Collect responses for each entry
            duration = 30

            for data in data_list:
                print("first group: ", data)
                # Extract fields from the data
                # course_id = data.get("course")
                group_id = data.get("group_id")
                room_no = data.get("room_no")
                panel_member_ids = data.get("panel_members", [])

                # Validate required fields
                if not all([scheduled_time, course_id, group_id, room_no]):
                    response_data.append({"error": "Missing required fields", "group_id": group_id})
                    continue

                # Fetch related objects
                try:
                    course = Course.objects.get(pk=course_id)
                    assessment = Assessment.objects.get(pk=assessment_id)
                    assessment.is_done = True
                    assessment.save()
                    student_group = Group.objects.get(pk=group_id)

                    # Create or update the Presentation instance
                    presentation = Presentation.objects.create(
                        scheduled_time=scheduled_time,
                        course=course,
                        assessment=assessment,
                        student_group=student_group,
                        room_no=room_no
                    )
                    scheduled_time += timedelta(minutes=duration)

                    # Link panel members (if any)
                    if panel_member_ids:
                        print("faculty id exists: ", panel_member_ids)
                        users = User.objects.filter(id__in=panel_member_ids)
                        # print("Users fetched: ", users)
                        panel_members = Faculty.objects.filter(faculty_id__in=panel_member_ids)
                        print("Panel members len: ", len(panel_members))
                        presentation.panel_members.set(panel_members)
                        print("Final presentation: ", presentation)

                    # Save the presentation
                    presentation.save()

                    response_data.append({"message": "Presentation submitted successfully", "group_id": group_id, "id": presentation.id})
                except ObjectDoesNotExist as e:
                    response_data.append({"error": str(e), "group_id": group_id})
                except Exception as e:
                    response_data.append({"error": str(e), "group_id": group_id})

            return JsonResponse(response_data, safe=False, status=207)  # 207 Multi-Status for partial success

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
from .models import Presentation
class GetScheduledPresentationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        presentations = Presentation.objects.filter(course__in=user.assigned_courses.all())
        serialized_data = PresentationSerializer(presentations, many=True)
        return Response(serialized_data.data)
            # faculty_ids = request.data['scheduled_time']
        # try:
        #     for facultyId in faculty_ids:
        #         faculty_id = Faculty.objects.get(faculty_id=facultyId)

        # except Faculty.DoesNotExist:
        #     return Response({"error": "Faculty not found"}, status=status.HTTP_404_NOT_FOUND)

from django.contrib.auth.decorators import login_required

# Student Stuff
from xauth.models import Student
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
# @login_required
# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticated])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_courses(request):
    try:           
        student = Student.objects.get(user=request.user)
        print("Student is: ", student)
        courses = Course.objects.filter(students=student)
        courses_list = [
                {
                    'id': course.course_id,
                    'code': course.course_code,
                    'name': course.course_name,
                    'degree': course.degree.degree_name,
                    'semester': course.semester.semester_name,
                    'credits': course.credits,
                    'section_name': course.section_name,
                }
                for course in courses
            ]
        print("course list: ", courses_list)
        return JsonResponse(courses_list, safe=False)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Student profile not found'}, status=404)
        
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def save_group(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             project_title = data.get('project_title')
#             course_id = data.get('course_id')
#             created_by_id = data.get('created_by')

#             course = get_object_or_404(Course, course_id=course_id)
#             created_by = get_object_or_404(Student, id=created_by_id)

#             group = Group.objects.create(
#                 project_title=project_title,
#                 course=course,
#                 created_by=created_by
#             )
#             return JsonResponse({'message': 'Group created successfully!', 'group_id': group.group_id}, status=201)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
from django.core.exceptions import PermissionDenied

# class StudentCoursesView(viewsets.ReadOnlyModelViewSet):
#     permission_classes = [IsAuthenticated]  
#     def get(self, request, *args, **kwargs):
#         # Get the logged-in student
#         try:
#             user = request.user
#             print("User is: ", user.username)
#             student = Student(user=user)
#         except Student.DoesNotExist:
#             raise PermissionDenied("User is not a student.")

#         # Fetch courses for this student
#         courses = Course.objects.filter(students=student).values('course_id', 'course_code', 'course_name')
#         return JsonResponse(list(courses), safe=False)
# from .serializers import GroupInvitationSerializer
# from .models import GroupInvitation
# class GroupInvitationView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
#     def get(self, request):
#         invitations = GroupInvitation.objects.all()
#         serializer = GroupInvitationSerializer(invitations, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = GroupInvitationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from .models import GroupInvitation
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def add_group_member(request):
    if request.method == 'POST':
        try:
            user = request.user
            # Parse the incoming JSON data from the request
            data = json.loads(request.body)

            sap_id = data.get('sapId')
            project_title = data.get('projectTitle')
            print("Sap id: ", sap_id, " title: ", project_title)

            # Validate input
            if not sap_id or not project_title:
                return JsonResponse({'error': 'SAP ID and Project Title are required'}, status=400)

            # Check if student exists with given SAP ID
            try:
                student = Student.objects.get(sap_id=sap_id)
                print("Student got: ", student)
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student with this SAP ID does not exist'}, status=404)
            sending_student = Student.objects.get(user=user)
            print("User requesting: ", sending_student)
            # Find or create a group with the project title (you might want to adjust this logic)
            group_received, _ = Group.objects.get_or_create(created_by=sending_student)
            print("Group: ", group_received)

            # Create the group invitation
            GroupInvitation.objects.create(group=group_received, invited_student=student, accepted=False)
            print("Created Successfully")
            return JsonResponse({'message': 'Group member added successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GroupInvitation

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_group_invitations(request):
    try:
        # Get the currently authenticated user
        user = request.user
        # Get the student's invitations
        student = Student.objects.get(user=user)
        invitations = GroupInvitation.objects.filter(invited_student=student, accepted=False)
        print("Invitations: ", invitations)
        # Prepare the data to send back
        invitations_data = []
        for invitation in invitations:
            invitations_data.append({
                'sapId': invitation.invited_student.sap_id,
                'projectTitle': invitation.group.project_title,
                'groupId': invitation.group.group_id,  # or other relevant group info
                'course': invitation.group.course.course_name  # Assuming there is a course related to the group
            })
        
        return Response(invitations_data, status=200)
    
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_group_invitation(request, invitation_id):
    try:
        # Get the invitation by ID
        invitation = GroupInvitation.objects.get(id=invitation_id)
        # Ensure the student is the invited student
        user = request.user
        student = Student.objects.get(user=user)
        
        if invitation.invited_student != student:
            return Response({'error': 'You are not invited to this group'}, status=403)
        
        # Accept the invitation
        invitation.accepted = True
        invitation.save()
        
        # Optionally, you can also add the student to the group members here, depending on your model
        
        return Response({'message': 'Invitation accepted'}, status=200)
    
    except GroupInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=404)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance, GroupMeeting
from .serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated

class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all attendance records
        attendances = Attendance.objects.all()
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)

class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Fetch a specific attendance record
        try:
            attendance = Attendance.objects.get(id=pk)
        except Attendance.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)

class MarkAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attendance_id):
        

        try:
            print("Im called")
            # Get meeting id, student id, and attendance status from the request
            print("meeting id: ", attendance_id)

            # student_id = request.data.get('student_id')
            is_present = request.data.get('is_present')
            print("is present: ", is_present)
            meeting = GroupMeeting.objects.get(id=attendance_id)
            print("This is meeting: ", meeting)
            attendance = Attendance.objects.get(meeting=meeting)
            attendance.is_present = is_present
            attendance.save()
            return Response({'status': 'Attendance updated successfully'})
        except GroupMeeting.DoesNotExist:
            return Response({"detail": "Meeting not found."}, status=status.HTTP_404_NOT_FOUND)

# from rest_framework import viewsets
# from .models import GroupMeeting, Attendance
# from .serializers import AttendanceSerializer
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import action

# class AttendanceViewSet(viewsets.ModelViewSet):
#     queryset = Attendance.objects.all()
#     serializer_class = AttendanceSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Filter based on past meetings
#         group_meeting_ids = GroupMeeting.objects.filter(status="Past").values_list('id', flat=True)
#         return Attendance.objects.filter(meeting__in=group_meeting_ids)

#     def perform_create(self, serializer):
#         # Logic for marking attendance goes here
#         serializer.save()
        
#     @action(detail=True, methods=['post'])
#     def mark_attendance(self, request, pk=None):
#         attendance = self.get_object()
#         is_present = request.data.get('is_present', False)
#         attendance.is_present = is_present
#         attendance.save()
#         return Response({"status": "Attendance updated"})


@permission_classes(["IsAuthenticated"])
@api_view(['GET'])
def evaluator_courses(request):
    evaluator = request.user
    faculty = Faculty.objects.get(user=evaluator)
    presentations = Presentation.objects.filter(panel_members=faculty)
    courses = {presentation.course for presentation in presentations}
    serializer = CourseSerializer(courses, many=True)
    print("presentations evaluator in: ", presentations)
    return Response(serializer.data)

@permission_classes(["IsAuthenticated"])
@api_view(['GET'])
def course_details(request, course_id, assessment_id):
    print("course ID received: ", course_id)
    course = Course.objects.get(course_id=course_id)
    groups = Group.objects.filter(course=course)
    assessment = Assessment.objects.get(course=course, assessment_id=assessment_id)
    criteria = AssessmentCriteria.objects.filter(assessment=assessment)
    print("Criteria: ", criteria)
    data = {
        'groups': [{'id': group.group_id, 'name': group.project_title} for group in groups],
        'criteria': [{'id': crit.criteria_id, 'name': crit.criteria, 'max_score': crit.max_score} for crit in criteria],
    }
    return Response(data)