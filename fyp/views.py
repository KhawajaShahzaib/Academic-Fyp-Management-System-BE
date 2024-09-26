from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import FYPIdea, Meeting, StudentGroup, Specialty, Request
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import FacultyDepartmentRole, Faculty, Role


@api_view(['POST'])  # Assuming this will be called after login
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def check_and_assign_supervisor_role(request):
    user = request.user  # Get the logged-in user

    print("Checking Role Assignment")

    
    # Check if the logged-in user is a faculty member
    if user.user_type == 'faculty':
        faculty = get_object_or_404(Faculty, user=user)
        
        # Check if the faculty has any role assigned
        role_assignment = FacultyDepartmentRole.objects.filter(faculty=faculty).first()
        if role_assignment is None:
            # If no role, assign the Supervisor role by default
            supervisor_role, created = Role.objects.get_or_create(role_name="Supervisor")
            department = faculty.department  # Assuming faculty already belongs to a department
            
            FacultyDepartmentRole.objects.create(faculty=faculty, department=department, role=supervisor_role)
            print(f"Supervisor role assigned to {user.username}")
            role_name = supervisor_role.role_name
        else:
            role_name = role_assignment.role.role_name  # Get the existing role name
        
        return JsonResponse({"role": role_name}, status=200)
    
    return JsonResponse({"message": "User is not a faculty member."}, status=403)

# FYPIdea Views
# class FYPIdeaListView(LoginRequiredMixin, ListView):
#     permission_classes = [IsAuthenticated]
#     model = FYPIdea

#     def get(self, request, *args, **kwargs):
#         return HttpResponse("List of FYPIdeas")

# class FYPIdeaCreateView(LoginRequiredMixin, CreateView):
#     permission_classes = [IsAuthenticated]
#     model = FYPIdea
#     fields = ['title', 'description', 'supervisor', 'domain', 'preferred_degree']
#     success_url = reverse_lazy('fypidea_list')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse("FYPIdea created")

# # Meeting Views
# class MeetingListView(LoginRequiredMixin, ListView):
#     permission_classes = [IsAuthenticated]
#     model = Meeting

#     def get(self, request, *args, **kwargs):
#         return HttpResponse("List of Meetings")

# class MeetingCreateView(LoginRequiredMixin, CreateView):
#     permission_classes = [IsAuthenticated]
#     model = Meeting
#     fields = ['group_name', 'date', 'time', 'status', 'supervisor']
#     success_url = reverse_lazy('meeting_list')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse("Meeting created")

# # StudentGroup Views
# class StudentGroupListView(LoginRequiredMixin, ListView):
#     permission_classes = [IsAuthenticated]
#     model = StudentGroup

#     def get(self, request, *args, **kwargs):
#         return HttpResponse("List of Student Groups")

# class StudentGroupCreateView(LoginRequiredMixin, CreateView):
#     permission_classes = [IsAuthenticated]
#     model = StudentGroup
#     fields = ['name', 'members']
#     success_url = reverse_lazy('studentgroup_list')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse("Student Group created")

# # Specialty Views
# class SpecialtyListView(LoginRequiredMixin, ListView):
#     permission_classes = [IsAuthenticated]
#     model = Specialty

#     def get(self, request, *args, **kwargs):
#         return HttpResponse("List of Specialties")

# class SpecialtyCreateView(LoginRequiredMixin, CreateView):
#     permission_classes = [IsAuthenticated]
#     model = Specialty
#     fields = ['name', 'supervisor']
#     success_url = reverse_lazy('specialty_list')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse("Specialty created")

# # Request Views
# class RequestListView(LoginRequiredMixin, ListView):
#     permission_classes = [IsAuthenticated]
#     model = Request

#     def get(self, request, *args, **kwargs):
#         return HttpResponse("List of Requests")

# class RequestCreateView(LoginRequiredMixin, CreateView):
#     permission_classes = [IsAuthenticated]
#     model = Request
#     fields = ['group_name', 'request_message', 'description', 'supervisor', 'members']
#     success_url = reverse_lazy('request_list')

#     def post(self, request, *args, **kwargs):
#         return HttpResponse("Request created")
