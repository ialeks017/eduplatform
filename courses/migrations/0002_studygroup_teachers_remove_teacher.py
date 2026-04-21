from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="studygroup",
            name="teachers",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={"role": "teacher"},
                related_name="taught_groups_new",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Преподаватели",
            ),
        ),
        migrations.RemoveField(
            model_name="studygroup",
            name="teacher",
        ),
        migrations.AlterField(
            model_name="studygroup",
            name="teachers",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to={"role": "teacher"},
                related_name="taught_groups",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Преподаватели",
            ),
        ),
    ]
