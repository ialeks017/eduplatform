from django.conf import settings
from django.db import models


class StudyGroup(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название группы")
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="taught_groups",
        limit_choices_to={"role": "teacher"},
        blank=True,
        verbose_name="Преподаватели",
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


class RecurringLessonPlan(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Понедельник"
        TUESDAY = 1, "Вторник"
        WEDNESDAY = 2, "Среда"
        THURSDAY = 3, "Четверг"
        FRIDAY = 4, "Пятница"
        SATURDAY = 5, "Суббота"
        SUNDAY = 6, "Воскресенье"

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="recurring_plans",
        verbose_name="Группа",
    )
    subject = models.CharField(max_length=20, choices=[("physics", "Физика"), ("math", "Математика"), ("cs", "Информатика")], verbose_name="Предмет")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices, verbose_name="День недели")
    starts_at = models.TimeField(verbose_name="Время начала")
    start_date = models.DateField(verbose_name="Дата начала расписания")
    end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания")
    duration_minutes = models.PositiveIntegerField(verbose_name="Длительность (мин)")
    cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Стоимость (руб)")
    description = models.TextField(blank=True, verbose_name="Описание урока")
    homework = models.TextField(blank=True, verbose_name="Домашнее задание")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_recurring_plans",
        verbose_name="Создал",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["weekday", "starts_at"]
        verbose_name = "Шаблон еженедельного занятия"
        verbose_name_plural = "Шаблоны еженедельных занятий"

    def __str__(self) -> str:
        return f"{self.group.name}: {self.get_subject_display()} ({self.get_weekday_display()} {self.starts_at:%H:%M})"


class Lesson(models.Model):
    class Subject(models.TextChoices):
        PHYSICS = "physics", "Физика"
        MATH = "math", "Математика"
        CS = "cs", "Информатика"

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликован"
        ARCHIVED = "archived", "Архив"

    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Группа",
    )
    source_plan = models.ForeignKey(
        RecurringLessonPlan,
        on_delete=models.SET_NULL,
        related_name="generated_lessons",
        null=True,
        blank=True,
        verbose_name="Шаблон расписания",
    )
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name="Запланировано на")
    subject = models.CharField(
        max_length=20,
        choices=Subject.choices,
        verbose_name="Предмет",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
        verbose_name="Статус",
    )
    duration_minutes = models.PositiveIntegerField(verbose_name="Длительность (мин)")
    cost = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Стоимость (руб)")
    description = models.TextField(blank=True, verbose_name="Описание урока")
    homework = models.TextField(blank=True, verbose_name="Домашнее задание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-scheduled_for", "-created_at"]
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        return f"{self.get_subject_display()} — {self.group.name}"


class LessonAttachment(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Урок",
    )
    file = models.FileField(upload_to="lesson_attachments/%Y/%m/%d", verbose_name="Файл")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружен")

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Файл урока"
        verbose_name_plural = "Файлы уроков"

    def __str__(self) -> str:
        return self.file.name.rsplit("/", maxsplit=1)[-1]


class VideoLesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название видеоурока")
    description = models.TextField(blank=True, verbose_name="Описание")
    video_file = models.FileField(upload_to="lesson_videos/%Y/%m/%d", verbose_name="Видео файл")
    groups = models.ManyToManyField(
        StudyGroup,
        related_name="video_lessons",
        verbose_name="Доступные группы",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_videos",
        verbose_name="Загрузил",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружен")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Видеоурок"
        verbose_name_plural = "Видеоуроки"

    def __str__(self) -> str:
        return self.title
