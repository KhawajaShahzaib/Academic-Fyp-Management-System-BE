from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import FacultyDepartmentRole, Role, Faculty

@receiver(user_logged_in)
def assign_supervisor_role(sender, user, **kwargs):
    print("Starting Signal Check")
    # Check if the logged-in user is a faculty member
    if user.user_type == 'faculty':
        # Check if the faculty has any role assigned
        faculty = Faculty.objects.get(user=user)
        if not FacultyDepartmentRole.objects.filter(faculty=faculty).exists():
            # If no role, assign the Supervisor role by default
            supervisor_role, created = Role.objects.get_or_create(role_name="Supervisor")
            # You can choose a department dynamically or use a default one
            department = faculty.department  # Assuming faculty already belongs to a department
            
            FacultyDepartmentRole.objects.create(faculty=faculty, department=department, role=supervisor_role)
            print(f"Supervisor role assigned to {user.username}")
