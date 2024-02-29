from django.urls import path, include, re_path
from . import views
from django.contrib import admin
from info.views import *
from info.signals import *

urlpatterns = [
    path('', views.index, name='index'),
    path('teacher/<slug:id_teacher>/t_timetable/', views.t_timetable, name='t_timetable'),
    path('teacher/<slug:id_teacher>/t_timetable/<slug:date>/<slug:next>', views.t_timetable_date_date, name='t_timetable_date_date'),
    path('student/<slug:id_group>/s_timetable/', views.s_timetable, name='s_timetable'),
    path('teacher/<slug:id_group>/s_timetable/<slug:date>/<slug:next>', views.s_timetable_date_date,
         name='s_timetable_date_date'),
    path('teacher/<slug:id_teacher>/LessonDates/', views.t_lesson_date, name='t_lesson_date'),
    path('teacher/<int:id_lesson>/Edit_att/', views.edit_att, name='edit_att'),
    path('teacher/<int:id_lesson>/attendance/confirm/', views.confirm, name='confirm'),
    path('teacher/<int:id_lesson>/attendance/create_att/', views.create_att, name='create_att'),
    path('teacher/<int:id_lesson>/attendance/create/', views.create, name='create'),
    path("t_timetable/<slug:id_lesson>/<slug:id_group>/<slug:date>/", views.t_create_lesson, name="t_create_lesson"),
    path("s_timetable/<slug:id_lesson>/<slug:id_group>/", views.s_create_lesson, name="s_create_lesson"),
    path('student/<int:id_lesson>/attendance/s_create_att/<int:id_group>/', views.s_create_att, name='s_create_att'),
    path('student/<int:id_lesson>/attendance/s_create/<int:id_group>/', views.s_create, name='s_create'),
    path('student/<int:id_lesson>/s_edit_att/', views.s_edit_att, name='s_edit_att'),
    path('student/<int:id_lesson>/attendance/confirm/', views.s_confirm, name='s_confirm'),
    path("student/stat", views.s_stat, name="s_stat"),
    path("teacher/subjects/", views.t_subjects, name="t_subjects"),
    path("teacher/subjects2/", views.t_subjects2, name="t_subjects2"),
    path("teacher/student/", views.t_stat_student, name="t_stat_student"),
    path("teacher/group/", views.t_stat_group, name="t_stat_group"),
    path("all_subjects/", views.all_subjects, name="all_subjects"),
    path("all_att/", views.all_att, name="all_att"),
    path("all_stat/", views.all_stat, name="all_stat"),
    path("all_stat_group/", views.all_stat_group, name="all_stat_group"),
    path("list_group/", views.list_group, name="list_group"),
    path("list_group_create/<slug:id_group>", views.list_group_create, name="list_group_create"),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('add_subjects/', views.add_subjects, name='add_subjects'),
    
    path('instruc/', views.instruc, name='instruc'),
    
    #path('artist/add/', views.artist_edit, name="artist-add"),
   

    #path('register/', views.register, name='register'),
    path('school_edit/<int:pk>', SchoolEditView.as_view(), name='school_edit'),
    path("school_view/", views.all_schools, name="school_view"),
    path("list_schools", views.list_schools, name="list_schools"),
]
    
    
    



