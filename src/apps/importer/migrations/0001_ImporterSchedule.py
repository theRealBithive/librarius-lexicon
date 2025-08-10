from django.db import migrations
from django.utils import timezone


def create_import_schedule(apps, schema_editor):
    Schedule = apps.get_model("django_q", "Schedule")
    # Avoid duplicate schedules if somehow re-run
    func_path = "src.apps.importer.main.import_audiobooks"
    if not Schedule.objects.filter(func=func_path).exists():
        Schedule.objects.create(
            name="Importer: import_audiobooks",
            func=func_path,
            schedule_type="I",
            minutes=15,
            next_run=timezone.now(),
            repeats=-1,
        )


def delete_import_schedule(apps, schema_editor):
    Schedule = apps.get_model("django_q", "Schedule")
    Schedule.objects.filter(func="src.apps.importer.main.import_audiobooks").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("django_q", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_import_schedule, delete_import_schedule),
    ]