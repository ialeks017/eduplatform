from django.conf import settings
from django.db import models


class StudyGroup(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название группы")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="taught_groups",
        limit_choices_to={"role": "teacher"},
        verbose_name="Преподаватель",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_groups",
        limit_choices_to={"role": "student"},
        blank=True,
        verbose_name="Ученики",
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Учебная группа"
        verbose_name_plural = "Учебные группы"

    def __str__(self) -> str:
        return self.name


class Lesson(models.Model):
    class Subject(models.TextChoices):
        PHYSICS = "physics", "Физика"
        MATH = "math", "Математика"
        CS = "cs", "Информатика"

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Группа",
    )
    subject = models.CharField(
        max_length=20,
        choices=Subject.choices,
        verbose_name="Предмет",
    )
    duration_minutes = models.PositiveIntegerField(verbose_name="Длительность (мин)")
    cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Стоимость (руб)")
    description = models.TextField(blank=True, verbose_name="Описание урока")
    homework = models.TextField(blank=True, verbose_name="Домашнее задание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        return f"{self.get_subject_display()} — {self.group.name}"
