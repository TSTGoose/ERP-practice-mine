# Generated by Django 4.1 on 2023-02-02 08:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0031_student_expelled'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='att_status',
            options={'ordering': ['id'], 'verbose_name_plural': 'Статусы'},
        ),
        migrations.CreateModel(
            name='Group_Contingent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_group', models.CharField(max_length=100, unique=True, verbose_name='Номер группы контингент')),
                ('name', models.CharField(max_length=200, verbose_name='Группа')),
                ('study_form', models.CharField(blank=True, max_length=200, verbose_name='Форма обучения')),
                ('level', models.CharField(blank=True, max_length=200, verbose_name='Уровень')),
                ('faculty', models.CharField(blank=True, max_length=200, verbose_name='Факультет')),
                ('department', models.CharField(blank=True, max_length=200, verbose_name='Подразделение')),
                ('full_string', models.CharField(blank=True, max_length=200, verbose_name='Специальность')),
                ('status', models.BooleanField(blank=True, default=False)),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.period', verbose_name='Период')),
                ('students', models.ManyToManyField(blank=True, to='info.student', verbose_name='Студенты')),
            ],
            options={
                'verbose_name_plural': 'Группа',
                'ordering': ['name'],
                'unique_together': {('id_group', 'name')},
            },
        ),
    ]
