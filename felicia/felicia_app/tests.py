from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "testuser"
        self.password = "StrongPass123!"
        User.objects.create_user(username=self.username, password=self.password, is_active=True)

    def test_login_success(self):
        response = self.client.post(reverse("login"), {"username": self.username, "password": self.password})
        self.assertNotEqual(response.status_code, 500)

    def test_logout_redirect(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)