# Generated by Django 4.1 on 2022-09-08 07:03

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_group', models.CharField(max_length=100, unique=True, verbose_name='Номер группы')),
                ('name', models.CharField(max_length=200, verbose_name='Группа')),
                ('year_priem', models.CharField(max_length=200, verbose_name='Год приема')),
            ],
            options={
                'verbose_name_plural': 'Группа',
                'unique_together': {('id_group', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Предмет',
            },
        ),
        migrations.CreateModel(
            name='Type_lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_type', models.CharField(max_length=100, unique=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Тип занятия')),
            ],
            options={
                'verbose_name_plural': 'Тип занятия',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_teacher', models.CharField(max_length=100, unique=True)),
                ('last_name', models.CharField(max_length=200, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=200, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=200, verbose_name='Отчество')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name_plural': 'Учитель',
            },
        ),
        migrations.CreateModel(
            name='Stuff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=200, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=200, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=200, verbose_name='Отчество')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name_plural': 'Управляющий',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_people', models.CharField(max_length=200, unique=True)),
                ('last_name', models.CharField(max_length=200, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=200, verbose_name='Имя')),
                ('second_name', models.CharField(max_length=200, verbose_name='Отчество')),
                ('starosta', models.BooleanField(blank=True, default=False)),
                ('id_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.group', verbose_name='Номер группы')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name_plural': 'Студент',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True, verbose_name='Номер Занятия')),
                ('topic', models.CharField(blank=True, max_length=200, verbose_name='Тема занятия')),
                ('date', models.DateField()),
                ('status', models.BooleanField(default=False)),
                ('id_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.group', verbose_name='Номер группы')),
                ('id_subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.subject', verbose_name='Предмет')),
                ('id_teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.teacher', verbose_name='ID учителя')),
                ('type', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='info.type_lesson', verbose_name='Тип занятия')),
            ],
            options={
                'verbose_name_plural': 'Занятие',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_create', models.DateField(auto_now_add=True, verbose_name='Время создания')),
                ('time_update', models.DateField(auto_now=True, verbose_name='Время обновления')),
                ('status', models.IntegerField(default=1, max_length=1, verbose_name='Статус')),
                ('id_lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.lesson', verbose_name='Номер Занятия')),
                ('id_student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.student', verbose_name='Номер Студента')),
            ],
            options={
                'verbose_name_plural': 'Посещаемость',
                'unique_together': {('id_lesson', 'id_student')},
            },
        ),
    ]
