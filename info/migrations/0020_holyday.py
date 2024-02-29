# Generated by Django 4.1 on 2022-11-21 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0019_student_subjects'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holyday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Праздник')),
                ('date', models.DateField(unique=True, verbose_name='Дата')),
            ],
            options={
                'verbose_name_plural': 'Выходные',
                'ordering': ['date'],
            },
        ),
    ]