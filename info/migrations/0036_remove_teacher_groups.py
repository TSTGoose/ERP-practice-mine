# Generated by Django 4.1 on 2023-02-05 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0035_alter_group_and_subject_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='groups',
        ),
    ]
