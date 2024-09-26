from django.contrib import admin
from .models import ProjectGroup, Role, FacultyDepartmentRole

# Registering the models in the admin panel
@admin.register(ProjectGroup)
class ProjectGroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'project_title', 'supervisor', 'department')
    search_fields = ('group_name', 'project_title', 'supervisor__user__username')
    list_filter = ('department', 'supervisor')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('role_name',)
    search_fields = ('role_name',)

@admin.register(FacultyDepartmentRole)
class FacultyDepartmentRoleAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'role', 'department')
    search_fields = ('faculty__user__username', 'role__role_name', 'department__department_name')
    list_filter = ('department', 'role')
