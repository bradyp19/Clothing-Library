from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
    
    def test_login_url_status_code(self):
        # Follow redirects so that a 301 is handled and final status is 200
        response = self.client.get(reverse('login:login'), follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_login_form_authentication(self):
        login_url = reverse('login:login')
        # Use 'login' field as expected by django-allauth instead of 'username'
        response = self.client.post(login_url, {
            'login': 'testuser',
            'password': 'testpass'
        }, follow=True)
        # Check that the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # The login view should redirect new users (with incomplete profiles)
        # to the profile setup page.
        self.assertRedirects(response, '/start/profile-setup/')
