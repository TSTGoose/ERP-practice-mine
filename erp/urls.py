from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from info.views import *
import info.views


urlpatterns = [
    #path('goderp/defender/', include('defender.urls')), # defender admin
    path('goderp/', admin.site.urls),
    
    path('', include('info.urls')),
    path('info/', include('info.urls')),
    #path('api/', include('apis.urls')),
    path('accounts/', include('registration.backends.default.urls')),
    path(r'select2/', include('django_select2.urls')),
    
    #path('accounts/login/', auth_views.LoginView.as_view(template_name='info/login.html'), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(template_name='info/logout.html'), name='logout'),
    path('accounts/password-change/', auth_views.PasswordChangeView.as_view(template_name='info/password_change_form.html'), name='password_change'),
    path('accounts/password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='info/password_change_done.html'), name='password_change_done'),
    re_path(r'group-autocomplete/', GroupAutocomplete.as_view(model=Group), name='group-autocomplete',),
    re_path(r'group-autocomplete_all/', GroupAutocomplete_all.as_view(model=Group), name='group-autocomplete_all',),
    re_path(r'subject-autocomplete/', SubjectAutocomplete.as_view(model=Subject), name='subject-autocomplete',),
    re_path(r'subject-autocomplete_all/', SubjectAutocomplete_all.as_view(model=Subject), name='subject-autocomplete_all',),
    re_path(r'teacher-autocomplete/', TeacherAutocomplete.as_view(model=Teacher), name='teacher-autocomplete',),
    re_path(r'student-autocomplete/', StudentAutocomplete.as_view(model=Student), name='student-autocomplete',),
    re_path(r'group_and_subjectautocomplete_all/', Group_and_SubjectAutocomplete_all.as_view(model=Group_and_Subject), name='group_and_subjectautocomplete_all',),
    re_path(r'group_and_subjectautocomplete/', Group_and_SubjectAutocomplete.as_view(model=Group_and_Subject), name='group_and_subjectautocomplete',),
    re_path(r'group_and_subjectautocomplete_student/', Group_and_SubjectAutocomplete_Student.as_view(model=Group_and_Subject), name='group_and_subjectautocomplete_student',),
    re_path(r'school_subject_dop/$', School_Subjects_dopAutocomplete_School.as_view(model=School_Subjects_dop), name='school_subject_dop',),
    re_path(r'school_subject/$', School_SubjectsAutocomplete_School.as_view(model=School_Subjects), name='school_subject',),

]