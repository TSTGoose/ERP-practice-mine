# Generated by Django 4.1 on 2023-02-15 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0043_attendance_changed_by_lesson_changed_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='status',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.DeleteModel(
            name='HistoricalUser',
        ),
    ]