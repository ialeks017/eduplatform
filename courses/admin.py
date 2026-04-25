from django.contrib import admin
from django.db.models import Count

from .models import Lesson, StudyGroup, VideoLesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ["subject", "duration_minutes", "cost", "description", "homework", "created_at"]
    readonly_fields = ["created_at"]
    show_change_link = True


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "teachers_count", "students_count", "lessons_count", "created_at"]
    list_filter = ["created_at", "teachers", "students"]
    search_fields = ["name", "description", "teachers__username", "students__username"]
    filter_horizontal = ["teachers", "students"]
    inlines = [LessonInline]
    readonly_fields = ["created_at"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _teachers_count=Count("teachers", distinct=True),
            _students_count=Count("students", distinct=True),
            _lessons_count=Count("lessons", distinct=True),
        )

    @admin.display(description="Преподавателей", ordering="_teachers_count")
    def teachers_count(self, obj):
        return obj._teachers_count

    @admin.display(description="Учеников", ordering="_students_count")
    def students_count(self, obj):
        return obj._students_count

    @admin.display(description="Уроков", ordering="_lessons_count")
    def lessons_count(self, obj):
        return obj._lessons_count


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "group",
        "duration_minutes",
        "cost",
        "created_at",
    ]
    list_filter = ["subject", "group", "created_at"]
    search_fields = ["group__name", "description", "homework"]
    autocomplete_fields = ["group"]
    readonly_fields = ["created_at"]


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ["title", "uploaded_by", "groups_count", "created_at"]
    list_filter = ["created_at", "groups", "uploaded_by"]
    search_fields = ["title", "description", "uploaded_by__username", "groups__name"]
    filter_horizontal = ["groups"]
    autocomplete_fields = ["uploaded_by"]
    readonly_fields = ["created_at"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(_groups_count=Count("groups", distinct=True))

    @admin.display(description="Групп", ordering="_groups_count")
    def groups_count(self, obj):
        return obj._groups_count
