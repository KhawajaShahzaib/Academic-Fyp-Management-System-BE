# from django.urls import path
# from .views import FYPIdeaCreateView, FYPIdeaListView, MeetingCreateView, MeetingListView

# urlpatterns = [
#     path('fypidea/create/', FYPIdeaCreateView.as_view(), name='fypidea_create'),
#     path('fypidea/list/', FYPIdeaListView.as_view(), name='fypidea_list'),
#     path('meeting/create/', MeetingCreateView.as_view(), name='meeting_create'),
#     path('meeting/list/', MeetingListView.as_view(), name='meeting_list'),
#     # Add the other paths similarly...
# ]
from django.urls import path
from . import views

# urlpatterns = [
#     path('fypideas/', views.FYPIdeaListView.as_view(), name='fypidea_list'),
#     path('fypideas/create/', views.FYPIdeaCreateView.as_view(), name='fypidea_create'),
#     path('meetings/', views.MeetingListView.as_view(), name='meeting_list'),
#     path('meetings/create/', views.MeetingCreateView.as_view(), name='meeting_create'),
#     path('student-groups/', views.StudentGroupListView.as_view(), name='studentgroup_list'),
#     path('student-groups/create/', views.StudentGroupCreateView.as_view(), name='studentgroup_create'),
#     path('specialties/', views.SpecialtyListView.as_view(), name='specialty_list'),
#     path('specialties/create/', views.SpecialtyCreateView.as_view(), name='specialty_create'),
#     path('requests/', views.RequestListView.as_view(), name='request_list'),
#     path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
#     path('check-and-assign-supervisor-role/', views.check_and_assign_supervisor_role, name='check-and-assign-supervisor-role'),
# ]

urlpatterns = [
    #For managing specialization of Supervisor
    path('check-and-assign-supervisor-role/', views.check_and_assign_supervisor_role, name='check-and-assign-supervisor-role'),
    path('update-supervisor-specialties/', views.update_supervisor_specialties, name='update-supervisor-specialties'),
    #For Supervision Request Handling
    path('get-supervision-requests/', views.get_supervision_requests, name='get-supervision-requests'),


     path('supervision-requests/', views.SupervisionRequestViewSet.as_view({'get': 'list'}), name='supervision-requests-list'),
    path('supervision-requests/<int:pk>/', views.SupervisionRequestViewSet.as_view({'patch': 'update'}), name='supervision-requests-update'),
    path('respond-to-supervision-request/<int:request_id>/', views.respond_to_supervision_request, name='respond-to-supervision-request'),

    #For Meetings
    
path('schedule-meetings/', views.MeetingViewSet.as_view({'post': 'create', 'get': 'list'}), name='schedule-meetings-list'),
path('groups/', views.GroupViewSet.as_view({'get': 'list'}), name='group-list'),
path('fyp-ideas/', views.FypIdeaViewSet.as_view({'post': 'create'}), name='fyp-ideas-create'), # POST for creating new ideas
# path('fyp-ideas/', views.FYPIdeaCreateView.as_view({'post': 'create'}), name='fyp-idea-create') # POST for creating new ideas

#For Director
path('courses-director/', views.CourseViewSet.as_view({'get': 'list'}), name='courses'),  # GET for listing, POST for creating
path('faculties/', views.FacultyViewSet.as_view({'get': 'list'}), name='faculties'),  # GET for listing, POST for creating
path('fyp-managers/', views.FypManagerViewSet.as_view({'post': 'create'}), name='fyp-managers'),  

#For FYP-Manager
path('courses/', views.get_courses, name='courses'),
path('submissions/', views.create_submission, name='create_submission'),
path('clos/', views.get_clos, name='get_clos'),
path('internal-assessment/', views.create_assessment_with_criteria, name='create_assessment_with_criteria'),  # Updated URL for creating a new assessmentD
path('<int:pk>/get-fyp-groups/', views.CourseViewSet.as_view({'get': 'get_fyp_groups'}), name='get-fyp-groups'),
path('assessment-questions/<int:assessment_id>/', views.AssessmentQuestionsView.as_view(), name='assessment-questions'),
path('assessment-questionsUpdate/<int:question_id>/', views.AssessmentCriteriaDetailView.as_view(), name='assessment-criteria-detail'),
path('assessments/', views.AssessmentView.as_view(), name='assessment_list_create'),  # For GET and POST
path('assessments/<int:pk>/', views.AssessmentView.as_view(), name='assessment_detail_update_delete'),  # For PUT and DELETE
path('upload_timetable/', views.TimetableUploadView.as_view(), name='TimetableUploadView'),
path('upload/', views.simple_upload, name='simple_upload'),

# For Fyp Ideas Sharing
]

