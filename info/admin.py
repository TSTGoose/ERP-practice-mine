
from datetime import timedelta, datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from django.http import HttpResponseRedirect
from django.urls import path
# Register your models here.
from .models import *


class LessonAdmin(admin.ModelAdmin):
    list_display = ('id_subject', 'id', 'id_lesson', 'id_group', 'period', 'date')
    readonly_fields = ('time_create', 'time_update',)
    search_fields = ['id_subject__name', 'id_group__name']

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'id_group', 'year_priem')
    ordering = ('year_priem',)
    search_fields = ['name']

class Group_ContingentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'id_group_rasp', 'id_group_contingent', 'period')
    ordering = ('name',)
    search_fields = ['name']

class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'id_people',)
    ordering = ('last_name',)
    search_fields = ['last_name', 'id_people']

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'format', 'user', 'time_create',)
    ordering = ('time_create',)
    search_fields = ['last_name', ]
    

class Type_lessonAdmin(admin.ModelAdmin):
    list_display = ('id_type', 'name',)

class Att_StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name',)

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'id_teacher', 'id')
    ordering = ('last_name',)
    search_fields = ['last_name','id_teacher']

class StafAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'id')
    ordering = ('last_name',)
    search_fields = ['last_name']

class SishAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'id')
    ordering = ('last_name',)
    search_fields = ['last_name']

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id_student', )
    ordering = ('-time_create',)
    search_fields = ['id_student']
    readonly_fields = ('time_create', 'time_update',)

class PeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)

class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)

class School_SubjectsAdmin(admin.ModelAdmin):
    list_display = ('name', 'id',)

class School_Subjects_dopAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_number','format', 'id',)

class HolydayAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'date')

class Group_and_SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'subject')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Group_Contingent, Group_ContingentAdmin)
admin.site.register(Type_lesson, Type_lessonAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Staf, StafAdmin)
admin.site.register(Sish, SishAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(School_Subjects, School_SubjectsAdmin)
admin.site.register(School_Subjects_dop, School_Subjects_dopAdmin)
admin.site.register(Lesson, LessonAdmin)
#admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Period, PeriodAdmin)
admin.site.register(Holyday, HolydayAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group_and_Subject, Group_and_SubjectAdmin)
admin.site.register(Att_Status, Att_StatusAdmin)
#admin.site.register(Lesson, SimpleHistoryAdmin)
admin.site.register(Attendance, SimpleHistoryAdmin)

