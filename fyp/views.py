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


from .serializers import SupervisionRequestSerializer, GroupMeetingSerializer, GroupSerializer, FypIdeaSerializer
from .serializers import SubmissionSerializer, AssessmentSerializer, AssessmentCriteriaSerializer, CLOSerializer, TimetableSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from django.utils.timezone import now

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
        serializer = self.get_serializer(data=request.data)
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
class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]  
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    def get_fyp_groups(self, request, pk=None):
        course = Course.objects.get(course_id=pk)
        projects = Group.objects.filter(course=course)
        # print("Projects: ", projects)
        serializer = GroupSerializer(projects, many=True)
        print("Serializer returning data: ", serializer.data)
        return Response(serializer.data)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses(request):
    user = request.user
    faculty = get_object_or_404(Faculty, user=user)
    # Fetch the FypManager record for the logged-in user
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


import openpyxl
from rest_framework.views import APIView

class TimetableUploadView(APIView):
    def post(self, request, *args, **kwargs):
        # Check if a file was uploaded
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Load the uploaded file
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            # Process the file data
            timetable_data = []
            for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header row
                teacher_name = row[0]
                day = row[1]
                time = row[2]

                # Store data in the database if needed or prepare it for response
                timetable_data.append({
                    "teacher_name": teacher_name,
                    "day": day,
                    "time": time
                })

            return Response({"message": "File processed successfully", "data": timetable_data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Failed to process the file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
