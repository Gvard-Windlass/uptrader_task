from django.test import TestCase, Client
from django.urls import reverse


class TestHomeView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        url = reverse("home")
        response = self.client.get(url)
        self.assertTrue(response.status_code, 200)
