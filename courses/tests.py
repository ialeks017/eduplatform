from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Lesson, StudyGroup

User = get_user_model()


class AdminStatisticsViewTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="Str0ng!Pass",
            role=User.Role.ADMIN,
        )
        self.teacher_1 = User.objects.create_user(
            username="teacher_1",
            password="Str0ng!Pass",
            role=User.Role.TEACHER,
            first_name="Иван",
            last_name="Иванов",
        )
        self.teacher_2 = User.objects.create_user(
            username="teacher_2",
            password="Str0ng!Pass",
            role=User.Role.TEACHER,
            first_name="Мария",
            last_name="Петрова",
        )

        self.group_1 = StudyGroup.objects.create(name="Группа 1")
        self.group_1.teachers.add(self.teacher_1)

        self.group_2 = StudyGroup.objects.create(name="Группа 2")
        self.group_2.teachers.add(self.teacher_2)

        Lesson.objects.create(
            group=self.group_1,
            subject=Lesson.Subject.MATH,
            duration_minutes=60,
            cost=2000,
        )
        Lesson.objects.create(
            group=self.group_1,
            subject=Lesson.Subject.CS,
            duration_minutes=90,
            cost=3200,
        )
        Lesson.objects.create(
            group=self.group_2,
            subject=Lesson.Subject.PHYSICS,
            duration_minutes=45,
            cost=1500,
        )

    def test_admin_can_view_statistics(self):
        self.client.login(username="admin", password="Str0ng!Pass")
        response = self.client.get(reverse("courses:statistics"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Статистика занятий")
        self.assertContains(response, "6700")

    def test_non_admin_has_no_access(self):
        self.client.login(username="teacher_1", password="Str0ng!Pass")

        response = self.client.get(reverse("courses:statistics"))
        self.assertEqual(response.status_code, 403)

    def test_filter_by_teacher(self):
        self.client.login(username="admin", password="Str0ng!Pass")

        response = self.client.get(reverse("courses:statistics"), {"teacher": self.teacher_1.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["overall"]["lessons_count"], 2)
        self.assertEqual(response.context["overall"]["total_duration"], 150)
        self.assertEqual(float(response.context["overall"]["total_cost"]), 5200.0)


class NavigationStatisticsLinkTest(TestCase):
    def test_admin_sees_statistics_link(self):
        admin = User.objects.create_user(
            username="admin_nav",
            password="Str0ng!Pass",
            role=User.Role.ADMIN,
        )
        self.client.force_login(admin)

        response = self.client.get(reverse("home"))
        self.assertContains(response, reverse("courses:statistics"))

    def test_non_admin_does_not_see_statistics_link(self):
        teacher = User.objects.create_user(
            username="teacher_nav",
            password="Str0ng!Pass",
            role=User.Role.TEACHER,
        )
        self.client.force_login(teacher)

        response = self.client.get(reverse("home"))
        self.assertNotContains(response, reverse("courses:statistics"))


class LessonEnhancementsTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher_feature",
            password="Str0ng!Pass",
            role=User.Role.TEACHER,
        )
        self.group = StudyGroup.objects.create(name="Алгебра 8А", description="Базовый курс")
        self.group.teachers.add(self.teacher)
        self.lesson = Lesson.objects.create(
            group=self.group,
            subject=Lesson.Subject.MATH,
            status=Lesson.Status.PUBLISHED,
            duration_minutes=60,
            cost=1500,
            description="Линейные уравнения",
            homework="Решить задачи 1-10",
        )
        self.client.force_login(self.teacher)

    def test_group_list_supports_search(self):
        response = self.client.get(reverse("courses:group_list"), {"q": "Алгебра"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Алгебра 8А")
        self.assertEqual(response.context["search_query"], "Алгебра")

    def test_teacher_can_duplicate_lesson(self):
        response = self.client.post(reverse("courses:lesson_duplicate", args=[self.lesson.pk]))

        self.assertEqual(response.status_code, 302)
        duplicated = Lesson.objects.exclude(pk=self.lesson.pk).get()
        self.assertEqual(duplicated.group, self.lesson.group)
        self.assertEqual(duplicated.subject, self.lesson.subject)
        self.assertEqual(duplicated.status, Lesson.Status.DRAFT)
