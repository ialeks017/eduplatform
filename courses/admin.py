from django.contrib import admin

from .models import Lesson, StudyGroup, VideoLesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["subject", "duration_minutes", "cost", "description", "homework"]


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    filter_horizontal = ["teachers", "students"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["__str__", "group", "subject", "duration_minutes", "cost", "created_at"]
    list_filter = ["subject", "group"]


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ["title", "uploaded_by", "created_at"]
    filter_horizontal = ["groups"]
