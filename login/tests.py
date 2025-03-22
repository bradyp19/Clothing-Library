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
        response = self.client.get(reverse('login:login'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_form_authentication(self):
        login_url = reverse('login:login')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        }, follow=True)
        # Check that the user is authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        # The login view should redirect new users (with incomplete profiles)
        # to the profile setup page.
        self.assertRedirects(response, '/start/profile-setup/')
