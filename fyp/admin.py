from django.contrib import admin
from .models import Role, FacultyDepartmentRole, Semester, Course, CLO, Assessment, AssessmentCriteria
from .models import  Group, GroupInvitation, GroupMembership
from .models import SupervisionRequest, Supervisor, Speciality, GroupMeeting, FYPIdea, Attendance

from .models import PanelInvitation, PanelMember, Presentation, Submission, SecondSupervisor, GroupMarks, FypManager, Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'is_present', 'assessment')
    list_filter = ('meeting', 'is_present')
    search_fields = ('meeting__group__project_title', 'assessment__title')  # Assuming 'title' is an attribute of Assessment
    autocomplete_fields = ['assessment']  # Useful if you have many assessments
    ordering = ['meeting', 'is_present']

admin.site.register(Attendance, AttendanceAdmin)
@admin.register(FYPIdea)
class FYPIdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'supervisor', 'domain', 'preferred_degree')  # Fields to display in the list view
    search_fields = ('title', 'description', 'domain')  # Fields to search
    list_filter = ('supervisor', 'domain')  # Fields to filter by

    # Optional: You can customize the form layout if needed
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'supervisor', 'domain', 'preferred_degree')
        }),
    )
class GroupMeetingAdmin(admin.ModelAdmin):
    list_display = ('group', 'date', 'time', 'status')
    list_filter = ('group', 'date', 'status')
    search_fields = ('group__project_title',)
    ordering = ('date', 'time')
    date_hierarchy = 'date'  # Enables a date-based drilldown in the admin interface

    def has_change_permission(self, request, obj=None):
        # Optionally restrict permissions
        if obj is not None and obj.status == 'Past':
            return False  # Prevent changing past meetings
        return super().has_change_permission(request, obj)

admin.site.register(GroupMeeting, GroupMeetingAdmin)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)

@admin.register(FacultyDepartmentRole)
class FacultyDepartmentRoleAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'role', 'department')
    search_fields = ('faculty__user__username', 'role__role_name', 'department__department_name')
    list_filter = ('department', 'role')

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_id', 'semester_name', 'start_date', 'end_date')
    search_fields = ('semester_name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_code', 'course_name', 'degree', 'semester', 'section_name', 'credits')
    list_filter = ('degree', 'semester')
    search_fields = ('course_code', 'course_name')
    filter_horizontal = ('students',)  # This will give you a horizontal filter box to add/remove students

@admin.register(CLO)
class CLOAdmin(admin.ModelAdmin):
    list_display = ('clo_id', 'title', 'clo_number', 'description', 'course')
    search_fields = ('description', 'title')
    list_filter = ('course',)

class AssessmentCriteriaInline(admin.TabularInline):
    model = AssessmentCriteria
    extra = 1  # Number of empty forms to display for criteria


class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'is_done', 'weightage')
    search_fields = ('name', 'description')
    list_filter = ('is_done', 'course')
    filter_horizontal = ('clos',)
    inlines = [AssessmentCriteriaInline]


class AssessmentCriteriaAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'criteria', 'max_score')
    list_filter = ('assessment',)
    search_fields = ('criteria', 'assessment__name')  # Allows searching by assessment name

# Register your models here
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(AssessmentCriteria, AssessmentCriteriaAdmin)


class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1  # Number of empty forms to display

    # Override save_related to ensure that memberships are saved after the group is created
    def save_related(self, request, formset, change):
        super().save_related(request, formset, change)  # Save the group first
        for group_membership in formset.save(commit=False):
            if group_membership.student and group_membership.student not in group_membership.group.members.all():
                group_membership.group = formset.instance  # Set the group instance
                group_membership.save()  # Save the membership

class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupMembershipInline]

admin.site.register(Group, GroupAdmin)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('group', 'student')
    search_fields = ('group__project_title', 'student__user__username')
    list_filter = ('group',)




@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('group', 'invited_student', 'accepted')
    search_fields = ('group__project_title', 'invited_student__user__username')
    list_filter = ('group', 'accepted')


#Supervisor Related:

@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display these fields in the list view
    search_fields = ('name',)  # Enable search functionality on the name field
    ordering = ('name',)  # Default ordering by name

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user',)  # Display the associated user in the list view
    search_fields = ('user__username',)  # Enable search on the username of the user associated with the supervisor
    list_filter = ('specialities',)  # Allow filtering by specialities
    ordering = ('user',)  # Default ordering by user
    filter_horizontal = ('specialities',)  # This will give you a horizontal filter box to add/remove students

class SupervisionRequestAdmin(admin.ModelAdmin):
    list_display = ('group', 'supervisor', 'status', 'request_message', 'description')
    list_filter = ('status', 'supervisor')
    search_fields = ('group__project_title', 'supervisor__name', 'status')
    ordering = ('status', 'group')




admin.site.register(SupervisionRequest, SupervisionRequestAdmin)


@admin.register(SecondSupervisor)
class SecondSupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'organization', 'is_approved')
    search_fields = ('name', 'email', 'organization')
    list_filter = ('is_approved',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'deadline')
    search_fields = ('title', 'course__course_name')

@admin.register(PanelMember)
class PanelMemberAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name__user__username',)

@admin.register(PanelInvitation)
class PanelInvitationAdmin(admin.ModelAdmin):
    list_display = ('panel_member', 'presentation', 'accepted')
    search_fields = ('panel_member__name__user__username', 'presentation__assessment__name')
    list_filter = ('accepted',)

@admin.register(GroupMarks)
class GroupMarksAdmin(admin.ModelAdmin):
    list_display = ('group', 'rubric', 'panel_member', 'marks')
    search_fields = ('group__project_title', 'rubric__assessment__name', 'panel_member__name__user__username')

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('scheduled_time', 'assessment', 'course', 'student_group', 'room_no', 'panel_members_display', 'feedback')
    search_fields = ('room_no', 'course__name', 'student_group__name')
    list_filter = ('scheduled_time', 'assessment', 'course', 'student_group')
    ordering = ('scheduled_time', 'course', 'room_no')

    def panel_members_display(self, obj):
        return ', '.join([faculty.user.username for faculty in obj.panel_members.all()])
    panel_members_display.short_description = 'Panel Members'

class FypManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'group_limit', 'group_size')  # Display these fields in the list view
    search_fields = ('user__user__username',)  # Search faculty by username
    filter_horizontal = ('course',)  # Allows multi-select for courses

admin.site.register(FypManager, FypManagerAdmin)

from .models import Timetable, TimetableEntry
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'file',)  # Display columns in the admin list view
    search_fields = ('course__name', 'file',)  # Enable search by course name and file field
    ordering = ('course',)  # Default ordering by course

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'room', 'day', 'time',)  # Display columns in the admin list view
    search_fields = ('teacher', 'room', 'day',)  # Enable search by teacher, room, and day
    list_filter = ('day', 'time',)  # Filter by day and time in the admin list view
    ordering = ('day', 'time',)  # Default ordering by day and time

from .models import Timetable_json
@admin.register(Timetable_json)
class Timetable_jsonAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'short_data')  # Display specific fields in admin list view
    search_fields = ('id', 'uploaded_at')  # Allow search by these fields

    def short_data(self, obj):
        """ Show a preview of the JSON data in the admin list. """
        return str(obj.data)[:100]  # Show a truncated version of the JSON data
