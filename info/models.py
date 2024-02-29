from django.db import models
import math
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from datetime import timedelta
from simple_history.models import HistoricalRecords
from simple_history import register
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import validators
# Create your models here.

time_slots = (
    ('08:30-10:05', '08:30-10:05'),
    ('10:15-11:50', '10:15-11:50'),
    ('12:50-14:25', '12:50-14:25'),
    ('14:35-16:10', '14:35-16:10'),
    ('16:20-17:55', '16:20-17:55'),
    ('18:00-19:35', '18:00-19:35'),
    ('19:45-21:20', '19:45-21:20'),
)


SCHOOL_CHOICES_CLASS_NUMBER =(
    ("1", "9 класс"),
    ("2", "10 класс"),
    ("3", "11 класс"),
)

SCHOOL_CHOICES_FORMAT =(
    ("1", "Онлайн"),
    ("2", "Офлайн"),
)

type_lessons = {
    2:'Лк',
    0:'Пр',
    1:'Лаб',
}

DAYS_OF_WEEK = (
    ('Time', "Время"),
    ('Monday', 'Понедельник'),
    ('Tuesday', 'Вторник'),
    ('Wednesday', 'Среда'),
    ('Thursday', 'Четверг'),
    ('Friday', 'Пятница'),
    ('Saturday', 'Суббота'),
)


class User(AbstractUser):
    @property
    def is_student(self):
        if hasattr(self, 'student'):
            return True
        return False

    @property
    def is_teacher(self):
        if hasattr(self, 'teacher'):
            return True
        return False

    @property
    def is_school(self):
        if hasattr(self, 'school'):
            return True
        return False

    @property
    def is_staf(self):
        if hasattr(self, 'staf'):
            return True
        return False
    
    @property
    def is_sish(self):
        if hasattr(self, 'sish'):
            return True
        return False


class Period(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Период')
    date_start = models.DateField(verbose_name='Дата начала', blank=True)
    date_end = models.DateField(verbose_name='Дата Конца', blank=True)
    term = models.CharField(max_length=2, verbose_name='Срок')

    class Meta:
        
        verbose_name_plural = 'Период'
        ordering = ['id']

    def __str__(self):
        return self.name


class Holyday(models.Model):
    name = models.CharField(max_length=200, verbose_name='Праздник')
    date = models.DateField(verbose_name='Дата', unique=True,)

    class Meta:
        
        verbose_name_plural = 'Выходные'
        ordering = ['date']

    def __str__(self):
        return self.name


class Att_Status(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название', unique=True)
    short_name = models.CharField(max_length=200, verbose_name='Короткое название')

    class Meta:
        
        verbose_name_plural = 'Статусы'
        ordering = ['id']

    def __str__(self):
        return self.name


class Post(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        
        verbose_name_plural = 'Должность'
        ordering = ['id']

    def __str__(self):
        return self.name


class Group(models.Model):
    # groups = models.ManyToManyField(Group, default=1)
    id_group = models.CharField(max_length=100, unique=True, verbose_name='Номер группы')
    name = models.CharField(max_length=200, verbose_name='Группа')
    year_priem = models.CharField(max_length=200, verbose_name='Год приема')
    study_form = models.CharField(max_length=200, blank=True, null=True, verbose_name='Форма обучения')
    level = models.CharField(max_length=200, blank=True, null=True, verbose_name='Уровень')
    faculty = models.CharField(max_length=200, blank=True, null=True, verbose_name='Факультет')
    department = models.CharField(max_length=200, blank=True, null=True, verbose_name='Подразделение')
    term_number = models.CharField(max_length=2, blank=True, verbose_name='Период')
    number_of_active_students = models.CharField(max_length=2, blank=True, verbose_name='Количество студентов')
    status = models.BooleanField(default=False, blank=True)
    semestr = models.CharField(max_length=10, blank=True, verbose_name='Семестр')

    class Meta:
        unique_together = [("id_group", "name")]
        verbose_name_plural = 'Группа'
        ordering = ['id_group']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        
        verbose_name_plural = 'Предмет'
        ordering = ['name']

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    id_people = models.CharField(max_length=200, unique=True)
    id_group = models.ForeignKey('Group_Contingent', on_delete=models.CASCADE, verbose_name='Номер группы', blank=True)
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Отчество')
    starosta = models.BooleanField(default=False, blank=True)
    subjects = models.ManyToManyField('Group_and_Subject', verbose_name='Предметы', blank=True)
    expelled = models.BooleanField(default=False, blank=True)
    passw = models.CharField(max_length=200, unique=False, blank=True)
    class Meta:
        
        verbose_name_plural = 'Студент'
        ordering = ['last_name']
    
    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.second_name


class Group_Contingent(models.Model):
    id_group_contingent = models.CharField(max_length=100, unique=True, verbose_name='Номер группы контингент')
    id_group_rasp = models.CharField(max_length=100, verbose_name='Номер группы расписание')
    name = models.CharField(max_length=200, verbose_name='Группа')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Период')
    study_form = models.CharField(max_length=200, blank=True, null=True, verbose_name='Форма обучения')
    level = models.CharField(max_length=200, blank=True, null=True, verbose_name='Уровень')
    faculty = models.CharField(max_length=200, blank=True, null=True, verbose_name='Факультет')
    department = models.CharField(max_length=200, blank=True, null=True, verbose_name='Подразделение')
    full_string = models.CharField(max_length=200, blank=True, null=True, verbose_name='Специальность')
    status = models.BooleanField(default=False, blank=True)
    students = models.ManyToManyField(Student, verbose_name='Студенты', blank=True)

    class Meta:
        unique_together = [("id_group_contingent", "id_group_rasp", "name")]
        verbose_name_plural = 'Группа'
        ordering = ['name']

    def __str__(self):
        return self.name


class Group_and_Subject(models.Model):
    group = models.ForeignKey(Group_Contingent, on_delete=models.CASCADE, verbose_name='Номер группы')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')

    class Meta:
        verbose_name_plural = 'Предметы по группам'
        unique_together = [("group", "subject")]
        ordering = ['subject']
    
    def __str__(self):
        return str(self.subject) + ' (' + str(self.group) + ')'


class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    id_teacher = models.CharField(max_length=100, unique=True)
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Отчество')
    groups = models.ManyToManyField(Group_Contingent, verbose_name='Группы', blank=True)
    subjects = models.ManyToManyField(Subject, verbose_name='Предметы', blank=True)
    group_and_subjects = models.ManyToManyField(Group_and_Subject, verbose_name='Предметы по группам', blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, verbose_name='Должность')
    status = models.BooleanField(default=True, blank=True)
    class Meta:
        
        verbose_name_plural = 'Учитель'
        ordering = ['last_name']

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.second_name


class Staf(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Отчество')

    class Meta:
        
        verbose_name_plural = 'Управляющий'

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.second_name


class Sish(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    last_name = models.CharField(max_length=200, verbose_name='Фамилия')
    first_name = models.CharField(max_length=200, verbose_name='Имя')
    second_name = models.CharField(max_length=200, verbose_name='Отчество')

    class Meta:
        
        verbose_name_plural = 'СИШ'

    def __str__(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.second_name


class Type_lesson(models.Model):
    id_type = models.CharField(max_length=100, unique=True, verbose_name='ID')
    name = models.CharField(max_length=200, unique=True, verbose_name='Тип занятия')

    class Meta:
        
        verbose_name_plural = 'Тип занятия'

    def __str__(self):
        return self.name   


class Lesson(models.Model):
    id_lesson = models.CharField(max_length=100, verbose_name='Номер Занятия в расписании')
    id_group = models.ForeignKey(Group_Contingent, on_delete=models.CASCADE, verbose_name='Номер группы')
    id_subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    id_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='ID учителя')
    type = models.ForeignKey(Type_lesson, on_delete=models.CASCADE, blank=True, verbose_name='Тип занятия')
    topic = models.CharField(max_length=200, blank=True, verbose_name='Тема занятия')
    date = models.DateField()
    status = models.BooleanField(default=False)
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Период')
    time_create = models.DateField(auto_now_add=True, blank=True, verbose_name='Время создания')
    time_update = models.DateField(auto_now=True, blank=True, verbose_name='Время обновления')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, verbose_name='Создал')
    history = HistoricalRecords()

    class Meta:
        
        verbose_name_plural = 'Занятие'
        ordering = ['-date']
    
    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.id_subject.name + ' - ' + self.id_group.name


class Attendance(models.Model):
    id_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Номер Занятия')
    id_student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Номер Студента')
    time_create = models.DateField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateField(auto_now=True, verbose_name='Время обновления')
    
    status = models.ForeignKey(Att_Status, on_delete=models.SET_DEFAULT, default=1, verbose_name='Статус')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, verbose_name='Создал')
    history = HistoricalRecords()

    class Meta:
        unique_together = [("id_lesson", "id_student")]
        verbose_name_plural = 'Посещаемость'
        #ordering = ['self.id_student.last_name']

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def __str__(self):
        return self.id_student.last_name + ' ' + self.id_student.first_name + ' ' + self.id_student.second_name


class School_Subjects(models.Model):
    name = models.CharField(max_length=154, unique=True)

    class Meta:
        verbose_name_plural = 'Предметы школьников'

    def __str__(self):
        return  self.name


class School_Subjects_dop(models.Model):
    subject = models.ForeignKey(School_Subjects, on_delete=models.CASCADE, verbose_name='Предмет')
    class_number = models.CharField(max_length=3, choices = SCHOOL_CHOICES_CLASS_NUMBER, verbose_name='Класс')
    format = models.CharField(max_length=10, choices = SCHOOL_CHOICES_FORMAT, verbose_name='Формат')

    class Meta:
        unique_together = [("subject", "class_number", "format")]
        verbose_name_plural = 'Дополнительные предметы'

    def __str__(self):
        return  str(self.subject) + ' (' + str(self.get_class_number_display()) + ' - ' + str(self.get_format_display()) + ' )'


class School(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    user_pass = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name='Пароль',
    )
    last_name = models.CharField(
        max_length=200, 
        verbose_name='Фамилия',
        validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Фамилия должна быть написана русскими буквами и начинаться с заглавной буквы')],
    )
    first_name = models.CharField(
        max_length=200, 
        verbose_name='Имя',
        validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Имя должно быть написано русскими буквами и начинаться с заглавной буквы')],
    )
    second_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name='Отчество',
        validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Отчество должно быть написано русскими буквами и начинаться с заглавной буквы')],
    )
    phone_number = models.CharField(
        max_length=200, 
        verbose_name='Номер телефона',
        validators=[
        validators.RegexValidator(
            regex=(r'^7\d{10}$'),
            message='Введите номер телефона в правильном формате',
            code='invalid_phone_number_parent'
        )],
    )
    date_of_birth = models.DateField( verbose_name='Дата рождения')
    town = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Город', 
        validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Город должен быть написан русскими буквами и начинаться с заглавной буквы')],
    )
    vk_link = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name='Ссылка на страницу в социальной сети ВКонтакте', 
        validators=[validators.URLValidator()]
    )
    fio_parent = models.CharField(
        max_length=200, 
        verbose_name='ФИО Родителя',
        validators=[validators.RegexValidator(regex=(r'[А-Я]{1}[а-я]+'), message='ФИО должно быть написано русскими буквами и начинаться с заглавной буквы')],
    )
    phone_number_parent = models.CharField(
        max_length=200, 
        verbose_name='Номер телефона Родителя', 
        validators=[
        validators.RegexValidator(
            regex=(r'^7\d{10}$'),
            message='Введите номер телефона в правильном формате',
            code='invalid_phone_number_parent'
        )],
    )
    school = models.CharField(max_length=200, verbose_name='Школа')
    class_number = models.CharField(max_length=3, choices = SCHOOL_CHOICES_CLASS_NUMBER, verbose_name='Класс')
    subject = models.ManyToManyField(School_Subjects, verbose_name='Предметы')
    format = models.CharField(max_length=10, choices = SCHOOL_CHOICES_FORMAT, verbose_name='Формат')
    time_create = models.DateField(auto_now_add=True, blank=True, verbose_name='Время создания')
    time_update = models.DateField(auto_now=True, blank=True, verbose_name='Время обновления')
    status = models.BooleanField(default=False, verbose_name='Активный')
    subject_dop = models.ManyToManyField(School_Subjects_dop, blank=True, verbose_name='Дополнительные предметы')

    class Meta:
        verbose_name_plural = 'Школьник'
        ordering = ['-time_create']
    
    def __str__(self):
        if (self.second_name):
            return self.last_name + ' ' + self.first_name + ' ' + self.second_name
        else:
            return self.last_name + ' ' + self.first_name

# Triggers
