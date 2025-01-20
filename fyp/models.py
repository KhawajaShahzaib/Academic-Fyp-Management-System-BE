from django.db import models
from django.conf import settings
from xauth.models import Student,  Department, Faculty, Degree

from django.core.exceptions import ValidationError
# Semester Model
class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    semester_name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.semester_name

# class DefaultCourses(models.Model):
#     course_id = models.AutoField(primary_key=True)
#     course_code = models.CharField(max_length=10)
#     course_name = models.CharField(max_length=100)
#     credits = models.PositiveIntegerField(default=3)

#     degree = models.ForeignKey(Degree, on_delete=models.CASCADE, default=1)

# Course Model
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=10)
    course_name = models.CharField(max_length=100)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, default=1)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, default=1)
    credits = models.PositiveIntegerField(default=3)
    students = models.ManyToManyField(Student)
    section_name = models.CharField(max_length=2)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
    #################################
    def save(self, *args, **kwargs):
        # Call the original save() method
        super().save(*args, **kwargs)

        # Check if the course name includes "Final Year Project"
        if "final year project" in self.course_name.lower():
            # Define the default assessments
            default_assessments = [
                {"name": "Attendance", "description": "Attendance of Students throught the fyp", "weightage": 10},
                {"name": "Proposal Defense", "description": "Evaluation of initial proposal", "weightage": 20},
                {"name": "Mid Term Evaluation", "description": "Mid-point progress review", "weightage": 30},
                {"name": "Final Evaluation", "description": "Comprehensive final review", "weightage": 40},
            ]

            # Create the assessments for this course if they don't exist already
            if not Assessment.objects.filter(course=self).exists():
                for assessment_data in default_assessments:
                    Assessment.objects.create(
                        name=assessment_data["name"],
                        course=self,
                        description=assessment_data["description"],
                        weightage=assessment_data["weightage"],
                        created_by=Faculty.objects.first()
                    )
    
class CLO(models.Model):
    clo_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)  # Adding a short title
    description = models.TextField()
    clo_number = models.PositiveIntegerField()
    course = models.ForeignKey(Course,  on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.description
    

# Project Group Model with Group Size Validation
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


class FypManager(models.Model):
    id = models.AutoField(primary_key=True)
    course =  models.ManyToManyField(Course, blank=True)
    # user = models.OneToOneField(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)
    group_limit = models.PositiveIntegerField(blank=True, null=True, default=3)
    group_size = models.PositiveIntegerField(blank=True, null=True, default=3)

class SecondSupervisor(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)
    supervisor_type = models.BooleanField(default=True) #True = Co Supervisor
    organization = models.CharField(max_length=200, blank=True, null=True)
    specialities = models.ManyToManyField('Speciality', related_name="external_supervisors", blank=True)
    is_approved = models.BooleanField(default=False)  # Approval flag

    def __str__(self):
        return f"{self.name} ({self.organization})"
 
class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    project_title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(Student, on_delete=models.CASCADE)
    # second_supervisor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, blank=True, null=True, related_name='co_supervisor')  # Optional Co-Supervisor
    second_supervisor = models.ForeignKey(SecondSupervisor, on_delete=models.SET_NULL, null=True, blank=True)  # Optional External Supervisor

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Group first
        # Check if the creator is already a member of the group
        if not GroupMembership.objects.filter(group=self, student=self.created_by).exists():
            GroupMembership.objects.create(group=self, student=self.created_by)

    def __str__(self):
        return f"{self.project_title}"

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='membership')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('group', 'student')  # Ensures a student can only join a group once

    def clean(self):
        # Custom validation to ensure no group has more than 3 members
        if self.group.membership.count() >= 3:
            raise ValidationError(f"The group '{self.group.project_title}' already has 3 members.")

    def save(self, *args, **kwargs):
        # Call the clean method before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} in {self.group.project_title}"
    

class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    invited_student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invitations')
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation to {self.invited_student.user.username} for {self.group.project_title}"

class Speciality(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Supervisor(models.Model):
    user = models.OneToOneField(Faculty, on_delete=models.CASCADE, related_name='supervisor_name')
    specialities = models.ManyToManyField(Speciality, related_name="supervisors", blank=True)

    def __str__(self):
        return self.user.user.username

class FYPIdea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
    domain = models.CharField(max_length=100)
    preferred_degree = models.CharField(max_length=100)  # Adjust as needed

    def __str__(self):
        return self.title

class SupervisionRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='supervision_requests')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    request_message = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')  # Can be 'pending', 'accepted', 'rejected'

    def __str__(self):
        return f"{self.group.project_title} - {self.status}"
from django.shortcuts import get_object_or_404


class Submission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    deadline = models.CharField(max_length=100)
    file = models.ImageField(upload_to="file")
    #MUST CHECK THROUGH VIEW IF THE CREATOR IS THE FYP MANAGER THROUGH THE CORUSE ID
    

    def str(self):
        return self.title
    

class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_done = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    presentation_required = models.BooleanField(default=False)
    weightage = models.FloatField(default=0.0)  # Weightage percentage
    course = models.ForeignKey(Course, on_delete=models.CASCADE) #Linked to semester
    clos = models.ManyToManyField(CLO, blank=True) 
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, default=1)
    def clean(self):
        # Calculate total weightage of all assessments for this course
        current_assessments = Assessment.objects.filter(course=self.course).exclude(assessment_id=self.assessment_id)
        total_weightage = sum(assessment.weightage for assessment in current_assessments)
        total_weightage += self.weightage  # Include the current assessment

        if total_weightage > 100:
            raise ValidationError(f"Total weightage for all assessments exceeds 100%. It is {total_weightage}%.")

    def save(self, *args, **kwargs):
        # Call the clean method before saving
        self.clean()
        super().save(*args, **kwargs)



    def __str__(self):
        return self.name


class AssessmentCriteria(models.Model): #Create for each assessment
    criteria_id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(Assessment, related_name='criteria', on_delete=models.CASCADE)
    criteria = models.CharField(max_length=100)
    max_score = models.FloatField(default=0.0)  # Max score for this criterion
    clo_link = models.ForeignKey(CLO, on_delete=models.SET_NULL, null=True)  # Link to CLO, see below

    def __str__(self):
        return f"{self.assessment.name} - {self.criteria}"

 
 #For Attendance Tracking

class GroupMeeting(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='meetings')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[('Upcoming', 'Upcoming'), ('Past', 'Past')])

    def clean(self):
        # Custom validation to ensure no two meetings are scheduled at the same time for the same group
        if GroupMeeting.objects.filter(group=self.group, date=self.date, time=self.time).exists():
            raise ValidationError(f"A meeting is already scheduled for {self.group.project_title} on {self.date} at {self.time}.")
    
    def save(self, *args, **kwargs):
        # Call the clean method before saving
        self.clean()
        super().save(*args, **kwargs)
        # Create attendance records for all students in the group
        course = self.group.course
        assessment = Assessment.objects.get(course=course, name='Attendance')
        print("Assessments: ", assessment)

        for membership in self.group.membership.all():
            attendance, created = Attendance.objects.get_or_create(meeting=self)
            if created:
                attendance.assessment = assessment  # Assuming Attendance has a field for Assessment
                attendance.save()


    def __str__(self):
        return f"Meeting for {self.group.project_title} on {self.date} at {self.time}"
class Attendance(models.Model):
    meeting = models.ForeignKey(GroupMeeting, on_delete=models.CASCADE, related_name='attendances')
    assessment = models.ForeignKey(Assessment, on_delete=models.SET_NULL, null=True, blank=True)  # Link to assessment if applicable

    is_present = models.BooleanField(default=False)  # Indicates if the student was present

    def __str__(self):
        return f"{self.meeting.group.project_title} on {self.meeting.date}"



class PanelMember(models.Model):
    name = models.OneToOneField(Faculty, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(Speciality, related_name="panelmembers", blank=True)

    def _str_(self):
        return self.name.user.username

class PanelInvitation(models.Model):
    panel_member = models.ForeignKey(PanelMember, on_delete=models.CASCADE)
    presentation = models.ForeignKey('Presentation', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, default=1)
    accepted = models.BooleanField(default=False)
    sender = models.ForeignKey(FypManager, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Allow null temporarily

class Presentation(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly set id as the primary key
    scheduled_time = models.DateTimeField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)  # Link to assessment if applicable
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    room_no = models.CharField(max_length=10)
    panel_members = models.ManyToManyField(Faculty, blank=True)
    feedback = models.TextField(blank=True, null=True)  # Feedback field, initially empty

    def __str__(self):
        return f"{self.assessment} - {self.scheduled_time}"

    def clean(self):
        super().clean()
        for member in self.panel_members.all():
            conflicts = Presentation.objects.filter(
                panel_members=member,
                scheduled_time=self.scheduled_time
            ).exclude(id=self.id)  # Exclude the current presentation if updating
            if conflicts.exists():
                raise ValidationError(
                    f"Panel member {member} is already assigned to another presentation at {self.scheduled_time}."
                )
 

class GroupMarks(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    rubric = models.ForeignKey(AssessmentCriteria, on_delete=models.CASCADE)  # The specific criterion
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # The group being evaluated
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    panel_member = models.ForeignKey(Faculty, on_delete=models.CASCADE)  # Panel member giving marks
    marks = models.FloatField()  # The marks given for that criterion
    

class Timetable(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    file = models.FileField(upload_to="timetables/")    

    def str(self):
        return self.file.name
    
class Timetable_json(models.Model):
    data = models.JSONField()  # To store the JSON data
    uploaded_at = models.DateTimeField(auto_now_add=True)
class TimetableEntry(models.Model):
    teacher = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    day = models.CharField(max_length=10)  # e.g., 'Monday'
    time = models.TimeField()
    # endtime = models.TimeField()

    def str(self):
        return self.teacher
