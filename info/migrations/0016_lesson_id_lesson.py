# Generated by Django 4.1 on 2022-11-07 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0015_alter_lesson_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='id_lesson',
            field=models.CharField(default=0, max_length=100, verbose_name='Номер Занятия в расписании'),
            preserve_default=False,
        ),
    ]
