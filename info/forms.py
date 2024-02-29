from random import choices
from django import forms
from .models import *
from dal import autocomplete
import datetime
from django.contrib.auth.forms import UserCreationForm 
from django.core.exceptions import ValidationError 
from django.core.management.base import BaseCommand
from registration.forms import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core import validators
from django_select2 import forms as s2forms
from django_select2.forms import ModelSelect2Widget
import re
from django.db.models import Q
date_end = datetime.datetime.today().year
date_start = date_end - 6


class DateInput(forms.DateInput):
        input_type = 'date'
        

class Att_Filter_Form(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    group = forms.ModelChoiceField(
            required=False,
            label='Группa',
            #queryset=Group.objects.filter(year_priem__range=(date_start, date_end), status=True),
            queryset=Group_Contingent.objects.all(),
            widget=autocomplete.ModelSelect2('group-autocomplete'),
    )
    subject = forms.ModelChoiceField(
            required=False,
            label='Предмет',
            queryset=Subject.objects.all(),
            widget=autocomplete.ModelSelect2('subject-autocomplete')
    )
    teacher = forms.ModelChoiceField(
            required=False,
            label='Преподаватель',
            queryset=Teacher.objects.filter(status=True),
            widget=autocomplete.ModelSelect2('teacher-autocomplete')
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    
    start_date = forms.DateField(
            label="Дата начала",
            required=False,
            widget=DateInput,
    )
    end_date = forms.DateField(
            label="Дата конца",
            required=False,
            widget=DateInput,
    )


class Att_Filter_All_Form(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    group = forms.ModelChoiceField(
            required=False,
            label='Группа',
            #queryset=Group.objects.filter(year_priem__range=(date_start, date_end), status=True),
            queryset=Group_Contingent.objects.all(),
            widget=autocomplete.ModelSelect2('group-autocomplete_all'),
    )
    subject = forms.ModelChoiceField(
            required=False,
            label='Предмет',
            queryset=Subject.objects.all(),
            widget=autocomplete.ModelSelect2('subject-autocomplete_all')
    )
    
    teacher = forms.ModelChoiceField(
            required=False,
            label='Преподаватель',
            queryset=Teacher.objects.filter(status=True),
            widget=autocomplete.ModelSelect2('teacher-autocomplete')
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    
    start_date = forms.DateField(
            label="Дата начала",
            required=False,
            widget=DateInput,
    )
    end_date = forms.DateField(
            label="Дата конца",
            required=False,
            widget=DateInput,
    )


class Subjects_Filter_All_Form(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=True,
            widget=autocomplete.ModelSelect2()
    )
    group_and_subject = forms.ModelChoiceField(
            
            label='Предмет',
            queryset=Group_and_Subject.objects.all(),
            widget=autocomplete.ModelSelect2('group_and_subjectautocomplete_all')
    )
    
    """teacher = forms.ModelChoiceField(
            
            label='Преподаватель',
            queryset=Teacher.objects.filter(status=True),
            widget=autocomplete.ModelSelect2('teacher-autocomplete')
    )"""
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    
    

class Subjects_Filter_Form(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=True,
            #widget=autocomplete.ModelSelect2()
            widget=ModelSelect2Widget(
                model=Period,
                search_fields=['name__icontains'],
                dependent_fields={'group__period': 'periods'},
                attrs={'class': 'select2',
                       'data-minimum-input-length': 0}
                
                )
    )
    
    group_and_subject = forms.ModelChoiceField(
            required=True,
            label='Предмет',
            queryset=Group_and_Subject.objects.all(),
            widget=ModelSelect2Widget(
                model=Group_and_Subject,
                search_fields=['name__icontains'],
                dependent_fields={'period': 'group__period'},
                attrs={'class': 'select2',
                       'data-minimum-input-length': 0}
                
                )
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") # store value of request 
        #print(self.request.user.teacher) 
        super().__init__(*args, **kwargs) 
        if self.request:
            self.fields['group_and_subject'].queryset = Teacher.objects.get(user=self.request.user).group_and_subjects.all()



class Lesson_Filter_Form(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    group = forms.ModelChoiceField(
            required=False,
            label='Группа',
            queryset=Group_Contingent.objects.all(),
            widget=autocomplete.ModelSelect2('group-autocomplete')
    )
    subject = forms.ModelChoiceField(
            required=False,
            label='Предмет',
            queryset=Subject.objects.all(),
            widget=autocomplete.ModelSelect2('subject-autocomplete')
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    
    start_date = forms.DateField(
            label="Дата начала",
            required=False,
            widget=DateInput,
    )
    end_date = forms.DateField(
            label="Дата конца",
            required=False,
            widget=DateInput,
    )

class Topic(forms.Form):
     class Meta:
        model = Lesson
        fields = [
            'topic',
            
        ]



class All_Stat(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    student = forms.ModelChoiceField(
            required=False,
            label='Студент',
            queryset=Student.objects.all(),
            widget=autocomplete.ModelSelect2('student-autocomplete')
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )

class All_Stat_Group(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            required=True,
            label="Период", 
            
            widget=autocomplete.ModelSelect2()
    )
    group = forms.ModelChoiceField(
            required=True,
            label='Группа',
            queryset=Group_Contingent.objects.all(),
            #widget=autocomplete.ModelSelect2('group-autocomplete')
            widget=ModelSelect2Widget(
                model=Group_Contingent,
                search_fields=['name__icontains'],
                dependent_fields={'period': 'period'},
                attrs={'class': 'select2',
                       'data-minimum-input-length': 0}
                
                )
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )

class Stat_Group(forms.Form):
    
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=True,
            #initial=Period.objects.last(),
            widget=autocomplete.ModelSelect2()
            #widget=ModelSelect2Widget(
                #model=Period,
                #search_fields=['name__icontains'],
                #)
    )
    group = forms.ModelChoiceField(
            required=True,
            label='Группа',
            queryset=Group_Contingent.objects.all(),
            #widget=autocomplete.ModelSelect2('group-autocomplete')
            widget=ModelSelect2Widget(
                model=Group_Contingent,
                search_fields=['name__icontains'],
                dependent_fields={'period': 'period'},
                attrs={'class': 'select2',
                       'data-minimum-input-length': 0}
                
                )
    )
    
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request") # store value of request 
        #print(self.request.user.teacher) 
        super().__init__(*args, **kwargs) 
        if self.request:
            self.fields['group'].queryset = Teacher.objects.get(user=self.request.user).groups.all()
            


#форма для статистики студента    
class S_Stat(forms.Form):
    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )
    type = forms.ModelChoiceField(
            queryset=Type_lesson.objects.all(), 
            label="Тип занятия", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )

class Add_Subjects(forms.Form):

    period = forms.ModelChoiceField(
            queryset=Period.objects.all().reverse(), 
            label="Период", 
            required=False,
            widget=autocomplete.ModelSelect2()
    )    
    student = forms.ModelChoiceField(
            
            label='Студент',
            queryset=Student.objects.all(),
            widget=autocomplete.ModelSelect2('student-autocomplete')
    )
    subject = forms.ModelChoiceField(
            
            label='Предмет',
            queryset=Group_and_Subject.objects.filter(group__period=Period.objects.last()),
            widget=autocomplete.ModelSelect2('group_and_subjectautocomplete_student')
    )

class List_Group_Form(forms.Form):
    group = forms.ModelChoiceField(
            required=False,
            label='Группа',
            #queryset=Group.objects.filter(year_priem__range=(date_start, date_end), status=True),
            queryset=Group_Contingent.objects.all(),
            widget=autocomplete.ModelSelect2('group-autocomplete'),
    )        
   
    


class CustomUserCreationForm(RegistrationFormUniqueEmail):
        username = forms.CharField(
             min_length=5,
             label='Логин',
             widget=forms.TextInput(attrs={'class': 'form-input',
                                           'placeholder': 'User_login',}
                                    ),
             validators=[validators.RegexValidator(regex=(r'([a-zA-Z0-9_])+'), message='Логин может состоять из английских букв и цифр')],
             
        )
        email = forms.EmailField(
             #max_length=7,
             
             label='E-mail',
             widget=forms.TextInput(attrs={'placeholder': 'Test@mail.ru'}),
        )

        password1 = forms.CharField(
             label='Пароль', 
             widget=forms.PasswordInput(attrs={'class': 'form-input'})
        )
        password2 = forms.CharField(
             label='Повтор пароля', 
             widget=forms.PasswordInput(attrs={'class': 'form-input'})
        )
        
        last_name = forms.CharField(
              max_length=200, 
              label='Фамилия', 
              widget=forms.TextInput(attrs={'placeholder': 'Иванов'}),
              validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Фамилия должна быть написана русскими буквами и начинаться с заглавной буквы')],
        )
        first_name = forms.CharField(
              max_length=200, 
              label='Имя', 
              widget=forms.TextInput(attrs={'placeholder': 'Иван'}),
              validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Имя должно быть написано русскими буквами и начинаться с заглавной буквы')],
        )
        second_name = forms.CharField(
              max_length=200, 
              label='Отчество', 
              required=False, 
              widget=forms.TextInput(attrs={'placeholder': 'Иванович'}),
              validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Отчество должно быть написано русскими буквами и начинаться с заглавной буквы')],
        )
        phone_number = forms.CharField(
             max_length=12,
             #error_messages={'required': 'Введите номер телефона в правильном формате'}, 
             #help_text='Формат +7xxxxxxxxxx', 
             label='Номер телефона', 
             validators=[validators.RegexValidator(regex=(r'^7\d{10}$'), message='Введите номер телефона в правильном формате 7XXXXXXXX')],
             #initial='+79234406382',
             widget=forms.TextInput(attrs={'placeholder': '7XXXXXXXX'}),
        )
        date_of_birth = forms.DateField(
            label="Дата рождения",
            required=False,
            widget=DateInput,
            initial='2011-11-11',
        )
        town = forms.CharField(
              max_length=200, 
              label='Город', 
              widget=forms.TextInput(attrs={'placeholder': 'Томск'}),
              validators=[validators.RegexValidator(regex=(r'([А-Я][а-я])+'), message='Город должен быть написан русскими буквами и начинаться с заглавной буквы')],
        )
        vk_link = forms.URLField(
             max_length=200, 
             label='Ссылка на страницу в социальной сети ВКонтакте', 
             required=False, 
             #validators=[validators.URLValidator()],
             widget=forms.TextInput(attrs={'placeholder': 'https://vk.com/id000000'}),
             )
        fio_parent = forms.CharField(
              max_length=200, 
              label='ФИО Родителя', 
              widget=forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
              validators=[validators.RegexValidator(regex=(r'[А-Я]{1}[а-я]+'), message='ФИО должно быть написано русскими буквами и начинаться с заглавной буквы')],)
        phone_number_parent = forms.CharField(
             max_length=12,
             #error_messages={'required': 'Введите номер телефона в правильном формате'}, 
             #help_text='Формат +7xxxxxxxxxx', 
             label='Номер телефона', 
             validators=[validators.RegexValidator(regex=(r'^7\d{10}$'), message='Введите номер телефона в правильном формате 7XXXXXXXX')],
             #initial='+79234406382',
             widget=forms.TextInput(attrs={'placeholder': '7XXXXXXXX'}),
        )
        school = forms.CharField(max_length=200, label='Школа', widget=forms.TextInput(attrs={'placeholder': 'Название школы'}),)
        class_number = forms.ChoiceField(choices = SCHOOL_CHOICES_CLASS_NUMBER, label='Класс')
        subject = forms.ModelMultipleChoiceField(queryset=School_Subjects.objects.filter(~Q(name='Информатика')), label='Предметы', widget=autocomplete.ModelSelect2Multiple(url='school_subject'),)
        
        format = forms.ChoiceField(choices = SCHOOL_CHOICES_FORMAT, label='Формат')
        subject_dop = forms.ModelMultipleChoiceField(
              queryset=School_Subjects_dop.objects.filter(~Q(subject__name='Информатика')),
              required=False,
              label='Дополнительные предметы', 
              widget=autocomplete.ModelSelect2Multiple(url='school_subject_dop'),
        )
        class Meta:
                model = User
                fields = ('username', 'password1', 'password2', 'email')
                widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-input'}),
        }
        # method for cleaning the data
        def clean(self):
                super(CustomUserCreationForm, self).clean()

                # getting username and password from cleaned_data
                username = self.cleaned_data.get('username')

                # validating the username and password
                
                if not re.fullmatch("([a-zA-Z0-9_])+", str(username)):
                        self._errors['username'] = self.error_class(['Логин должен содержать английские буквы и цифры'])
                        if len(username) < 5:
                                self._errors['username'] = self.error_class(['Логин должен содержать минимум 5 символов'])

                return self.cleaned_data
        
        
                
#[validators.RegexValidator(regex=(r'[a-zA-Z0-9_]'), message='Логин может состоять из английских букв и цифр')],
class SchoolForm(forms.ModelForm):
        def clean_due_back(self):
                last_name = self.cleaned_data['last_name']
                
                if last_name[0].islower():
                        raise ValidationError(('Фамилия не может начинаться с маленькой буквы.'))
                return last_name
        class Meta:
                model = School
                fields = '__all__'
                exclude = ['user', 'status', 'user_pass']
                widgets = {
                'subject': autocomplete.ModelSelect2Multiple(url='school_subject'),
                'date_of_birth': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
                'subject_dop': autocomplete.ModelSelect2Multiple(url='school_subject_dop'),
                        
                        
                }
                
class View_Schools(forms.Form):
    
    start_date = forms.DateField(
            label="Дата начала",
            required=False,
            widget=DateInput,
    )
    end_date = forms.DateField(
            label="Дата конца",
            required=False,
            widget=DateInput,
    )    
        
