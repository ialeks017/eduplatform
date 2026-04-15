from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Администратор"
        TEACHER = "teacher", "Преподаватель"
        STUDENT = "student", "Ученик"
        GUEST = "guest", "Гость"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GUEST,
        verbose_name="Роль",
    )

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
