from django.db import models
from django.conf import settings
from xauth.models import Student, User, Department, Faculty

from django.core.exceptions import ValidationError

# Project Group Model with Group Size Validation
class ProjectGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    group_name = models.CharField(max_length=100)
    project_title = models.CharField(max_length=200)
    supervisor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

    # Validation to ensure group size does not exceed 3
    def clean(self):
        if self.students.count() > 3:
            raise ValidationError('Group size cannot exceed 3 students.')

    def __str__(self):
        return f"{self.group_name} - {self.project_title} - {self.supervisor.user.username}"

# Role Model (No change here)
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role_name

# Faculty Role for specific Department (Allowing multiple roles per faculty per department)
class FacultyDepartmentRole(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.faculty.user.username} - {self.role.role_name} ({self.department.department_name})"

    class Meta:
        unique_together = ('faculty', 'department', 'role')  # Ensures unique role assignment per department

# class Group(models.Model):
#     department = models.ForeignKey(Department, on_delete=models.CASCADE)
#     project_title = models.CharField(max_length=50)
#     student_1 = models.ForeignKey(Student, related_name='group_student1', on_delete=models.CASCADE, null=True)
#     student_2 = models.ForeignKey(Student, related_name='group_student2', on_delete=models.CASCADE, null=True)
#     student_3 = models.ForeignKey(Student, related_name='group_student3', on_delete=models.CASCADE, null=True)
#     supervisor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)  # If supervisor can be null
 
#     def __str__(self):
#         return f"{self.project_title} - {self.department.department_name}"

class FYPIdea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    domain = models.CharField(max_length=100)
    preferred_degree = models.CharField(max_length=100)  # Adjust as needed

    def __str__(self):
        return self.title


class Meeting(models.Model):
    group_name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, default='Upcoming')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'Meeting with {self.group_name} on {self.date} at {self.time}'


class StudentGroup(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name


class Specialty(models.Model):
    name = models.CharField(max_length=100)
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Request(models.Model):
    group_name = models.CharField(max_length=100)
    request_message = models.TextField()
    description = models.TextField()
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.JSONField()  # or create a separate model for members

    def __str__(self):
        return f'Request from {self.group_name}'
    


