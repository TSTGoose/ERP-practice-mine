# Generated by Django 4.1 on 2024-02-19 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0052_alter_school_options_school_town_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='passw',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
