from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import FYPIdea, Meeting, StudentGroup, Specialty, Request

class FYPIdeaViewTests(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required email argument
            password='password'
        )
        self.client.login(username='testuser', password='password')

    def test_fypidea_list_view(self):
        response = self.client.get(reverse('fypidea_list'))
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List of FYPIdeas")

    def test_fypidea_create_view(self):
        response = self.client.post(reverse('fypidea_create'), {
            'title': 'Test Idea',
            'description': 'Description of test idea',
            'supervisor': self.user.id,
            'domain': 'Test Domain',
            'preferred_degree': 'Test Degree'
        })
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "FYPIdea created")
        self.assertTrue(FYPIdea.objects.filter(title='Test Idea').exists())

class MeetingViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required email argument

            password='password'
        )
        self.client.login(username='testuser', password='password')

    def test_meeting_list_view(self):
        response = self.client.get(reverse('meeting_list'))
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List of Meetings")

    def test_meeting_create_view(self):
        response = self.client.post(reverse('meeting_create'), {
            'group_name': 'Test Group',
            'date': '2024-10-01',
            'time': '14:00',
            'status': 'Upcoming',
            'supervisor': self.user.id
        })
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meeting created")
        self.assertTrue(Meeting.objects.filter(group_name='Test Group').exists())

class StudentGroupViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required email argument
            password='password'
        )
        self.client.login(username='testuser', password='password')

    def test_studentgroup_list_view(self):
        response = self.client.get(reverse('studentgroup_list'))
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List of Student Groups")

    def test_studentgroup_create_view(self):
        response = self.client.post(reverse('studentgroup_create'), {
            'name': 'Test Group',
            'members': [self.user.id]
        })
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student Group created")
        self.assertTrue(StudentGroup.objects.filter(name='Test Group').exists())

class SpecialtyViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required email argument
            password='password'
        )
        self.client.login(username='testuser', password='password')

    def test_specialty_list_view(self):
        response = self.client.get(reverse('specialty_list'))
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List of Specialties")

    def test_specialty_create_view(self):
        response = self.client.post(reverse('specialty_create'), {
            'name': 'Test Specialty',
            'supervisor': self.user.id
        })
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Specialty created")
        self.assertTrue(Specialty.objects.filter(name='Test Specialty').exists())

class RequestViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Required email argument
            password='password'
        )
        self.client.login(username='testuser', password='password')

    def test_request_list_view(self):
        response = self.client.get(reverse('request_list'))
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "List of Requests")

    def test_request_create_view(self):
        response = self.client.post(reverse('request_create'), {
            'group_name': 'Test Group',
            'request_message': 'Request message',
            'description': 'Request description',
            'supervisor': self.user.id,
            'members': ['member1', 'member2']  # Replace with appropriate member IDs
        })
        print(response.content.decode())  # Print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Request created")
        self.assertTrue(Request.objects.filter(group_name='Test Group').exists())
