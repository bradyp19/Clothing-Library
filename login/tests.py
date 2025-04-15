from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

@override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        # Mark the email as verified (for completeness, though not needed with verification off)
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True,
        )
    
    def test_login_url_status_code(self):
        response = self.client.get(reverse('login:login'), follow=True)
        self.assertEqual(response.status_code, 200)
    
    # def test_login_form_authentication(self):
    #     login_url = reverse('login:login')
    #     response = self.client.post(login_url, {
    #         'login': 'test@example.com',  # using email per allauth default behavior
    #         'password': 'testpass'
    #     }, follow=True)
    #     # Check that the user is authenticated
    #     self.assertTrue(response.wsgi_request.user.is_authenticated)
    #     # The login view should redirect to the profile setup page
    #     self.assertRedirects(response, '/start/profile-setup/')
