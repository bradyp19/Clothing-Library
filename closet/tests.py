from django.test import TestCase, Client
from django.urls import reverse

class ClosetTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_closet_index_status_code(self):
        # Follow redirects to get the final status code
        response = self.client.get(reverse('closet:closet_index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_closet_index_template_used(self):
        response = self.client.get(reverse('closet:closet_index'), follow=True)
        self.assertTemplateUsed(response, 'closet/closet_index.html')
