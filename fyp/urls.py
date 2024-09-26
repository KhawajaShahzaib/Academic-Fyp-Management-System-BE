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

    path('check-and-assign-supervisor-role/', views.check_and_assign_supervisor_role, name='check-and-assign-supervisor-role'),
]