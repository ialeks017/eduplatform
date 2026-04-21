from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    def test_default_role_is_guest(self):
        user = User.objects.create_user(username="testuser", password="pass123!")
        self.assertEqual(user.role, User.Role.GUEST)

    def test_str_includes_username_and_role(self):
        user = User.objects.create_user(username="alice", password="pass123!", role=User.Role.STUDENT)
        self.assertIn("alice", str(user))
        self.assertIn("Ученик", str(user))


class SignUpViewTest(TestCase):
    def test_signup_creates_user_and_redirects(self):
        response = self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Str0ng!Pass",
            "password2": "Str0ng!Pass",
        })
        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_logs_in_user(self):
        self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Str0ng!Pass",
            "password2": "Str0ng!Pass",
        })
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_signup_weak_password_fails(self):
        response = self.client.post(reverse("signup"), {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "123",
            "password2": "123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="Str0ng!Pass")

    def test_profile_requires_login(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username="alice", password="Str0ng!Pass")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", email="alice@example.com", password="Str0ng!Pass"
        )

    def test_password_reset_page_loads(self):
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_with_valid_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))

    def test_password_reset_with_unknown_email_still_redirects(self):
        # Security: не раскрываем, существует ли email
        response = self.client.post(reverse("password_reset"), {"email": "unknown@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
