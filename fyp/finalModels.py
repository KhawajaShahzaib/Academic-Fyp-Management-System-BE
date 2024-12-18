from django.db import models
from django.conf import settings
from xauth.models import Student, User, Department, Faculty, Degree

from django.core.exceptions import ValidationError
# Semester Model
class Semester(models.Model):
    semester_id = models.AutoField(primary_key=True)
    semester_name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.semester_name
    

# Course Model
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=10)
    course_name = models.CharField(max_length=100)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    credits = models.PositiveIntegerField(default=3)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"
    
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




class CLO(models.Model):
    clo_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)  # Adding a short title
    description = models.TextField()
    clo_number = models.PositiveIntegerField()
    course = models.ForeignKey(Course,  on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.description
    
class FypManager(models.Model):
    id = models.AutoField(primary_key=True)
    course =  models.ManyToManyField(Course, blank=True)
    user = models.OneToOneField(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    group_limit = models.PositiveIntegerField(blank=True, null=True, default=3)
    group_size = models.PositiveIntegerField(blank=True, null=True, default=3)


 
class Group(models.Model):
    group_id = models.AutoField(primary_key=True)
    project_title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(Faculty, on_delete=models.CASCADE, blank=True, null=True)
    created_by = models.ForeignKey(Student, on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)  # Save the Group first
    #     # Automatically add the creator as a member of the group
    #     GroupMembership.objects.create(group=self, student=self.created_by)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Group first
        # Check if the creator is already a member of the group
        if not GroupMembership.objects.filter(group=self, student=self.created_by).exists():
            GroupMembership.objects.create(group=self, student=self.created_by)

    def __str__(self):
        return f"{self.project_title}"

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('group', 'student')  # Ensures a student can only join a group once

    def clean(self):
        # Custom validation to ensure no group has more than 3 members
        if self.group.members.count() >= 3:
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
    user = models.OneToOneField(Faculty, on_delete=models.CASCADE)
    specialities = models.ManyToManyField(Speciality, related_name="supervisors", blank=True)

    def __str__(self):
        return self.user.user.username


    

class SupervisionRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='supervision_requests')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    request_message = models.TextField()
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')  # Can be 'pending', 'accepted', 'rejected'

    def __str__(self):
        return f"{self.group.project_title} - {self.status}"
    
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
        for membership in self.group.members.all():
            Attendance.objects.get_or_create(meeting=self)



    def __str__(self):
        return f"Meeting for {self.group.project_title} on {self.date} at {self.time}"


class PanelMember(models.Model):
    name = models.OneToOneField(Faculty, on_delete=models.CASCADE)
    expertise = models.ManyToManyField(Speciality, related_name="panelmembers", blank=True)

    def _str_(self):
        return self.name.user.username

class PanelInvitation(models.Model):
    panel_member = models.ForeignKey(PanelMember, on_delete=models.CASCADE)
    presentation = models.ForeignKey('Presentation', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    sender = models.ForeignKey(FypManager, on_delete=models.SET_NULL, null=True, blank=True)

class Assessment(models.Model):
    assessment_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    is_done = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    presentation_required = models.BooleanField(default=False)
    weightage = models.FloatField(default=0.0)  # Weightage percentage
    course = models.ForeignKey(Course, on_delete=models.CASCADE) #Linked to semester
    clos = models.ManyToManyField(CLO, blank=True)
    created_by = models.ForeignKey(Faculty, on_delete=models.CASCADE)



    def __str__(self):
        return self.name


class AssessmentCriteria(models.Model): #Create for each assessment
    criteria_id = models.AutoField(primary_key=True)
    assessment = models.ForeignKey(Assessment, related_name='criteria', on_delete=models.CASCADE)
    criteria = models.CharField(max_length=100)
  
    max_score = models.FloatField(default=0.0)  # Max score for this criterion
    clo_link = models.ForeignKey(CLO, on_delete=models.SET_NULL, null=True)  # Link to CLO, see below

    def __str__(self):
        return f"{self.assessment.name} - {self.name}"
 
class GroupMarks(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)  # The group being evaluated
    rubric = models.ForeignKey(AssessmentCriteria, on_delete=models.CASCADE)  # The specific criterion
    panel_member = models.ForeignKey(PanelMember, on_delete=models.CASCADE)  # Panel member giving marks
    marks_awarded = models.FloatField()  # The marks given for that criterion



#For Attendance Tracking
class Attendance(models.Model):
    meeting = models.ForeignKey(GroupMeeting, on_delete=models.CASCADE, related_name='attendances')
    assessment = models.ForeignKey(Assessment, on_delete=models.SET_NULL, null=True, blank=True)  # Link to assessment if applicable

    is_present = models.BooleanField(default=False)  # Indicates if the student was present

    # class Meta:
    #     unique_together = ('meeting', 'student')  # Ensures a student can only have one attendance entry per meeting

    def __str__(self):
        return f"{self.meeting.group.project_title} on {self.meeting.date}"



class FYPIdea(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True)
    domain = models.CharField(max_length=100)
    preferred_degree = models.CharField(max_length=100)  # Adjust as needed

    def __str__(self):
        return self.title
    

class Submission(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    deadline = models.CharField(max_length=100)
    file = models.ImageField(upload_to="file")
    #MUST CHECK THROUGH VIEW IF THE CREATOR IS THE FYP MANAGER THROUGH THE CORUSE ID
    

    def str(self):
        return self.title
    

class Presentation(models.Model):
    scheduled_time = models.DateTimeField()
    assessment = models.ForeignKey(Assessment, on_delete=models.SET_NULL)  # Link to assessment if applicable
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    # student_group = models.CharField(max_length=100)
    room_no = models.CharField(max_length=10)
    created_by = models.ForeignKey(FypManager, on_delete=models.SET_NULL)
    # panel_members = models.ForeignKey(FacultyDepartmentRole, on_delete=models.CASCADE)

    # panel_members = models.ManyToManyField('Facultys', blank=True)

    def str(self):
        return self.title
 