from tokenize import group
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import *
from .forms import *
from django.db.models import Q, Exists, Subquery
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import requests
import datetime
from collections import defaultdict
# Create your views here.
from dal import autocomplete
import io
from django.views.generic.edit import UpdateView
from django.views.generic import View
import xlsxwriter
from django.contrib import messages
from registration.views import *

from .utils import pars_timetable

User = get_user_model()


# Create your views here.


@login_required
def index(request):
    if request.user.is_staf and request.user.is_teacher:
        return render(request, 'info/t_homepage.html')
    if request.user.is_staf:
        return render(request, 'info/staf_homepage.html')
    if request.user.is_teacher:
        return render(request, 'info/t_homepage.html')
    if request.user.is_student:
        return render(request, 'info/s_homepage.html')
    if request.user.is_school:
        return render(request, 'info/school_homepage.html')
    if request.user.is_superuser:
        return render(request, 'info/admin_page.html')
    return render(request, 'info/logout.html')


@login_required
def instruc(request):
    return render(request, 'info/instruc.html')

@login_required()
def t_timetable(request, id_teacher):
    if not request.user.is_teacher:
        return redirect("/")
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    rp = requests.get(f'http://raspisanie.ssti.ru/data.php?teacher_week={request.user.teacher.id_teacher}&date={date}',
                      verify=False)
    lesson = []
    groups = []
    groups_name = []
    days_week = []
    class_matrix = [[i for i in range(7)] for j in range(7)]
    start_week = rp.json()['start']
    format = '%Y-%m-%d'
    for i in range(0, 6):
        days = datetime.datetime.strptime(start_week, format)
        days_week.append((days + datetime.timedelta(int(i))).strftime('%d.%m'))
    DAYS_OF_WEEK = (
        ('Time', "Время"),
        ('Monday', f'Понедельник, {days_week[0]}'),
        ('Tuesday', f'Вторник, {days_week[1]}'),
        ('Wednesday', f'Среда, {days_week[2]}'),
        ('Thursday', f'Четверг, {days_week[3]}'),
        ('Friday', f'Пятница, {days_week[4]}'),
        ('Saturday', f'Суббота, {days_week[5]}'),
    )
    for i, d in enumerate(time_slots):

        for j in range(7):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            for k in rp.json()['data']:
                if int(k['weekday']) == j and int(k['para']) - 1 == i:
                    for h in k['groups']:
                        groups.append(h['id'])
                        groups_name.append(h['name'])
                    list = dict(pairs=zip(k['id'].split(','), groups, groups_name))
                    date = ("-").join(k['date'].split('.')[::-1])
                    format = '%Y-%m-%d'
                    date_lesson = datetime.datetime.strptime(date, format)
                    lesson.append({
                        'subject': k['subject'],
                        'weekday': k['weekday'],
                        'date': k['date'],
                        'id': k['id'].split(','),
                        'para': k['para'],
                        'type': int(k['type']),
                        'groups': groups,
                        'list': list,
                        'cancel': k['cancel'],
                        'holyday': Holyday.objects.filter(date=date_lesson).exists(),
                    })
                    groups = []
                    groups_name = []
                    class_matrix[i][j] = lesson
            lesson = []

    context = {
        'time_slots': class_matrix,
        'days': DAYS_OF_WEEK,
        'time': time_slots,
        'date': date,
        'next': +7,
        'previous': -7,
        'week': rp.json()['week'],
    }
    return render(request, 'info/t_timetable.html', context)


# Есть функция вывода расписания для учители и студента
# Есть отдельная функция, которая парсит расписание в зависимости от недели
# Отличия между этими двумя функциями только в том, что первая парсит за текущую неделю, а вторая, парсит за выбранную (период 7 дней в + или -)
# Там и там используется переменная date
# Следовательно, можно проверять, если переменная date передаётся, то значит неделю нужно сменить. Если нет, то по умолчанию выставляется today

# Изменить код так, чтоб он оставался в функциональной парадигме (хотя всё равно ей не следует)


@login_required()
def t_timetable_date_date(request, id_teacher, date, next):
    print("Next" + next)
    if not request.user.is_teacher:
        return redirect("/")
    return pars_timetable(request=request, id_teacher=id_teacher, date=date, next=next)


def s_timetable_date_date(request, id_group, date, next):
    print("Дата в запросе" + date)
    is_student = request.user.is_student;
    if not is_student and int(id_group) != int(request.user.student.id_group.id_group_rasp):
        return redirect("/")
    return pars_timetable(request=request, id_group=id_group, date=date, next=next)


@login_required()
def s_timetable(request, id_group):
    # Проверка: является пользователь студентом и совпадает ли переданная группа с группой студента
    is_student = request.user.is_student;
    if not is_student and int(id_group) != int(request.user.student.id_group.id_group_rasp):
        return redirect("/")
    return pars_timetable(request=request, id_group=id_group)


@login_required()
def t_lesson_date(request, id_teacher):
    if not request.user.is_teacher:
        return redirect("/")
    if int(id_teacher) != int(request.user.teacher.id_teacher):
        return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    form = Lesson_Filter_Form(request.GET)
    lessons = Lesson.objects.filter(id_teacher=Teacher.objects.get(id_teacher=id_teacher))
    for sub in request.user.teacher.group_and_subjects.all():
        lessons = lessons | Lesson.objects.filter(id_group=sub.group, id_subject=sub.subject)

    if request.method == 'GET':
        if 'group' in request.GET and request.GET['group']:
            get_group = request.GET['group']
            lessons = lessons.filter(id_group=get_group)
        if 'subject' in request.GET and request.GET['subject']:
            get_subject = request.GET['subject']
            lessons = lessons.filter(id_subject=get_subject)
        if 'type' in request.GET and request.GET['type']:
            get_type = request.GET['type']
            lessons = lessons.filter(type=get_type)
        if 'period' in request.GET and request.GET['period']:
            period = request.GET['period']
            lessons = lessons.filter(period=period)
        if 'end_date' in request.GET and request.GET['end_date'] and not request.GET['start_date']:
            get_end_date = (request.GET['end_date'])
            lessons = lessons.filter(date__lte=get_end_date)
        if 'start_date' in request.GET and request.GET['start_date']:
            get_start_date = (request.GET['start_date'])
            lessons = lessons.filter(date__gte=get_start_date)
            if 'end_date' in request.GET and request.GET['end_date']:
                get_end_date = (request.GET['end_date'])
                lessons = lessons.filter(date__range=(get_start_date, get_end_date))

    att = {}
    for lesson in lessons:
        out = Attendance.objects.filter(id_lesson=lesson.id, status=0)
        present = Attendance.objects.filter(id_lesson=lesson.id, status=1)
        late = Attendance.objects.filter(id_lesson=lesson.id, status=2)
        half = Attendance.objects.filter(id_lesson=lesson.id, status=3)

        att.update({
            lesson.id: {
                'out': len(out),
                'present': len(present),
                'late': len(late),
                'half': len(half),
            }})
    group_and_subjects = []
    for lesson in lessons:
        group_and_subject = Group_and_Subject.objects.filter(subject=lesson.id_subject, group=lesson.id_group)
        group_and_subjects.append(group_and_subject)

    context = {
        'lesson_list': lessons,
        'atts': att,
        'form': form,
        'group_and_subject': group_and_subjects,

    }
    return render(request, 'info/t_lesson_date.html', context=context)


@login_required()
def create_att(request, id_lesson):
    print(Lesson.objects.get(id=id_lesson).id_teacher.id_teacher)
    if not request.user.is_teacher:
        return redirect("/")

    if Lesson.objects.get(
            id=id_lesson).id_subject not in request.user.teacher.subjects.all() and not request.user.is_staf:
        return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    if Attendance.objects.filter(id_lesson=get_object_or_404(Lesson, id=id_lesson)):
        return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
    att_status = Att_Status.objects.all()
    lesson = Lesson.objects.get(id=id_lesson)
    students = lesson.id_group.students.order_by('last_name')

    subject = Group_and_Subject.objects.get(subject=lesson.id_subject, group=lesson.id_group)

    context = {
        'students': students,
        'id': id_lesson,
        'subject': subject,
        'att_status': att_status,

    }

    return render(request, 'info/t_create_att.html', context)


@login_required()
def create(request, id_lesson):
    print(id_lesson)
    if not request.user.is_teacher:
        return redirect("/")
    if int(Lesson.objects.get(id=id_lesson).id_teacher.id_teacher) != int(
            request.user.teacher.id_teacher) and not request.user.is_staf:
        return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    lesson = Lesson.objects.get(id=id_lesson)
    students = lesson.id_group.students.all()
    if lesson.date < Period.objects.last().date_start or lesson.date > Period.objects.last().date_end:
        return render(request, 'info/dont_create_lesson.html', {'title': 'период аттестации закончен'}, )
    lesson.topic = request.POST['topic']
    lesson.status = 1

    lesson.save()
    if not Attendance.objects.filter(id_lesson=get_object_or_404(Lesson, id=id_lesson)):
        for i in (students):
            # print(i.subjects.filter(subject=lesson.id_subject).first())
            if i.subjects.filter(subject=lesson.id_subject, group=lesson.id_group).first():
                status = Att_Status.objects.get(name='Перезачтено')
            else:
                status = Att_Status.objects.get(id=request.POST[i.id_people])
            try:
                Attendance.objects.create(status=status, id_lesson=get_object_or_404(Lesson, id=id_lesson),
                                          id_student=get_object_or_404(Student, id_people=i.id_people),
                                          changed_by=request.user)
                # return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
            except Exception as e:
                print(e, 'errrrrrrrrrrrrrrrrrrrrrrrrrr')
                return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
def edit_att(request, id_lesson):
    if not request.user.is_teacher and not request.user.is_staf:
        return redirect("/")
    if Lesson.objects.get(
            id=id_lesson).id_subject not in request.user.teacher.subjects.all() and not request.user.is_staf:
        return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    att_list = Attendance.objects.filter(id_lesson=id_lesson).order_by('id_student__last_name')
    att_status = Att_Status.objects.all()
    lesson = Lesson.objects.get(id=id_lesson)
    context = {
        'att_list': att_list,
        'id': id_lesson,
        'lesson': lesson,
        'att_status': att_status,
    }
    return render(request, 'info/t_edit_att.html', context)


@login_required()
def confirm(request, id_lesson):
    if not request.user.is_teacher:
        return redirect("/")
    if Lesson.objects.get(
            id=id_lesson).id_subject not in request.user.teacher.subjects.all() and not request.user.is_staf:
        return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    att = Attendance.objects.filter(id_lesson=id_lesson)
    lesson = Lesson.objects.get(id=id_lesson)
    lesson.type = Type_lesson.objects.get(id=1)
    lesson.save()
    if lesson.date < Period.objects.last().date_start or lesson.date > Period.objects.last().date_end:
        return render(request, 'info/dont_create_lesson.html', {'title': 'период аттестации закончен'}, )
    for i, s in enumerate(att):
        if s.id_student.subjects.filter(subject=lesson.id_subject, group=lesson.id_group).first():
            status = Att_Status.objects.get(name='Перезачтено')
        else:
            status = Att_Status.objects.get(id=request.POST[s.id_student.id_people])
        try:
            a = Attendance.objects.get(id_student=s.id_student, id_lesson=id_lesson)
            a.status = status
            a.save()
        except Attendance.DoesNotExist:
            a = Attendance(id_student=s.id_student)
            a.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
def t_create_lesson(request, id_lesson, id_group, date):
    if not request.user.is_teacher:
        return redirect("/")
    period = Period.objects.last()
    flag = False
    rp = requests.get(f'http://raspisanie.ssti.ru/data.php?teacher_week={request.user.teacher.id_teacher}&date={date}',
                      verify=False)
    for k in rp.json()['data']:
        for teach in k['teachers']:
            # print(teach)
            if teach['id'] == request.user.teacher.id_teacher:
                flag = True
        if flag == False:
            return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
        for n in k['id'].split(','):
            if k['cancel'] == '0' and n == id_lesson:
                return render(request, 'info/dont_create_lesson.html', {'title': 'занятие было отменено'}, )
            if n == id_lesson:
                date = ("-").join(k['date'].split('.')[::-1])
                format = '%Y-%m-%d'
                date_lesson = datetime.datetime.strptime(date, format)
                # print(date_lesson, Holyday.objects.filter(date=date_lesson).exists())
                # print(date_lesson.date(), 'f', period.date_start)
                if date_lesson.date() < period.date_start or date_lesson.date() > period.date_end:
                    return render(request, 'info/dont_create_lesson.html', {'title': 'неверный период аттестации'}, )
                if date_lesson > (datetime.datetime.today()):
                    return render(request, 'info/dont_create_lesson.html',
                                  {'title': 'день проведения занятия еще не наступил '}, )
                if Holyday.objects.filter(date=date_lesson).exists():
                    return render(request, 'info/dont_create_lesson.html',
                                  {'title': 'в данный день занятие не проводилось'}, )
                for h in k['groups']:
                    if h['id'] == id_group:
                        try:
                            if Lesson.objects.filter(id_lesson=id_lesson, date=date):
                                if Attendance.objects.filter(id_lesson=id_lesson):
                                    return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
                                else:
                                    # print('est')
                                    lesson = Lesson.objects.get(id_lesson=id_lesson, date=date)
                                    return HttpResponseRedirect(reverse('create_att', args=(lesson.id,)))
                            new_lesson = Lesson.objects.create(id_lesson=id_lesson,
                                                               id_group=get_object_or_404(Group_Contingent,
                                                                                          id_group_rasp=id_group,
                                                                                          period=period),
                                                               id_subject=get_object_or_404(Subject, name=k['subject']),
                                                               type=get_object_or_404(Type_lesson, id_type=k['type']),
                                                               date=date, id_teacher=get_object_or_404(Teacher,
                                                                                                       id_teacher=request.user.teacher.id_teacher),
                                                               period=Period.objects.last(), changed_by=request.user)
                            # print(new_lesson.id)
                            # print('sozdal')
                            return HttpResponseRedirect(reverse('create_att', args=(new_lesson.id,)))
                        except Exception as e:
                            # print(e, 'errrrrrrrrrrrrrrrrrrrrrrrrrr')
                            if Attendance.objects.filter(id_lesson=id_lesson):
                                return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
                            else:
                                # print('zx')
                                return HttpResponseRedirect(reverse('create_att', args=(id_lesson,)))


@login_required()
def s_create_lesson(request, id_lesson, id_group):
    period = Period.objects.last()
    if not request.user.student.starosta == True:
        return redirect("/")
    if int(id_group) != int(request.user.student.id_group.id_group_rasp):
        return render(request, 'info/dont_create_lesson.html', {'title': 'не удалось создать'}, )
    rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={id_group}', verify=False)
    for k in rp.json()['data']:

        if k['teachers']:
            teacher = k['teachers'][0]['id']
        else:
            teacher = 0
        if "href" in k['subject']:
            subject = k['subject'].split('>')[1].split('<')[0]
        else:
            subject = k['subject']
        # print(subject)
        for n in k['id'].split(','):
            if k['cancel'] == '0' and n == id_lesson:
                return render(request, 'info/dont_create_lesson.html', {'title': 'занятие было отменено'}, )
            if n == id_lesson:
                date = ("-").join(k['date'].split('.')[::-1])
                format = '%Y-%m-%d'
                date_lesson = datetime.datetime.strptime(date, format)
                if date_lesson > (datetime.datetime.today()):
                    return render(request, 'info/dont_create_lesson.html', {'title': 'занятие еще не наступило'}, )
                for h in k['groups']:
                    if h['id'] == id_group:

                        try:
                            if Lesson.objects.filter(id_lesson=id_lesson, date=date):
                                if Attendance.objects.filter(id_lesson=id_lesson):
                                    return HttpResponseRedirect(reverse('s_timetable', args=(id_group,)))
                                else:
                                    lesson = Lesson.objects.get(id_lesson=id_lesson, date=date)

                                    return HttpResponseRedirect(reverse('s_create_att', args=(lesson.id, id_group)))
                            new_lesson = Lesson.objects.create(id_lesson=id_lesson,
                                                               id_group=get_object_or_404(Group_Contingent,
                                                                                          id_group_rasp=id_group,
                                                                                          period=period),
                                                               id_subject=get_object_or_404(Subject, name=subject),
                                                               type=get_object_or_404(Type_lesson, id_type=k['type']),
                                                               date=date, id_teacher=get_object_or_404(Teacher,
                                                                                                       id_teacher=teacher),
                                                               period=Period.objects.last(), changed_by=request.user)

                            return HttpResponseRedirect(reverse('s_create_att', args=(new_lesson.id, id_group)))
                        except Exception as err:
                            print(err)
                            if Attendance.objects.filter(id_lesson=id_lesson):
                                return HttpResponseRedirect(reverse('s_timetable', args=(id_group,)))
                            else:
                                return HttpResponseRedirect(reverse('s_create_att', args=(id_lesson, id_group)))


@login_required()
def s_create_att(request, id_lesson, id_group):
    if not request.user.student.starosta == True:
        return redirect("/")
    if int(id_group) != int(request.user.student.id_group.id_group_rasp):
        return redirect("/")
    if Attendance.objects.filter(id_lesson=id_lesson):
        return HttpResponseRedirect(reverse('s_edit_att', args=(id_lesson,)))
    att_status = Att_Status.objects.all()
    lesson = Lesson.objects.get(id=id_lesson)
    students = lesson.id_group.students.order_by('last_name')
    subject = Group_and_Subject.objects.get(subject=lesson.id_subject, group=lesson.id_group)
    context = {
        'students': students,
        'id': id_lesson,
        'id_group': id_group,
        'subject': subject,
        'att_status': att_status,
    }

    return render(request, 'info/s_create_att.html', context)


@login_required()
def s_create(request, id_lesson, id_group):
    if not request.user.student.starosta == True:
        return redirect("/")
    if int(id_group) != int(request.user.student.id_group.id_group_rasp):
        return redirect("/")

    lesson = Lesson.objects.get(id=id_lesson)
    students = lesson.id_group.students.all()
    lesson.topic = request.POST['topic']
    lesson.status = 1
    lesson.save()
    if not Attendance.objects.filter(id_lesson=get_object_or_404(Lesson, id=id_lesson)):
        for i in (students):
            # print(i.subjects.filter(subject=lesson.id_subject).first())
            if i.subjects.filter(subject=lesson.id_subject, group=lesson.id_group).first():
                status = Att_Status.objects.get(name='Перезачтено')
            else:
                status = Att_Status.objects.get(id=request.POST[i.id_people])
            try:

                Attendance.objects.create(status=status, id_lesson=get_object_or_404(Lesson, id=id_lesson),
                                          id_student=get_object_or_404(Student, id_people=i.id_people),
                                          changed_by=request.user)
                # return HttpResponseRedirect(reverse('edit_att', args=(id_lesson,)))
            except Exception as e:
                print(e, 'errrrrrrrrrrrrrrrrrrrrrrrrrr')
                return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('s_timetable', args=(id_group,)))


@login_required()
def s_edit_att(request, id_lesson):
    if not request.user.student.starosta == True:
        return redirect("/")
    # if Lesson.objects.get(id=id_lesson).id_subject not in request.user.teacher.subjects.all() and not request.user.is_staf:
    # return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    att_list = Attendance.objects.filter(id_lesson=id_lesson).order_by('id_student__last_name')
    att_status = Att_Status.objects.all()
    lesson = Lesson.objects.get(id=id_lesson)

    if lesson.date < (datetime.date.today()):
        return render(request, 'info/dont_create_lesson.html', {'title': 'занятие уже прошло'}, )
    context = {
        'att_list': att_list,
        'id': id_lesson,
        'lesson': lesson,
        'att_status': att_status,
    }
    return render(request, 'info/s_edit_att.html', context)


@login_required()
def s_confirm(request, id_lesson):
    if not request.user.student.starosta == True:
        return redirect("/")
    # if Lesson.objects.get(id=id_lesson).id_subject not in request.user.teacher.subjects.all() and not request.user.is_staf:
    # return HttpResponseRedirect(reverse('t_lesson_date', args=(request.user.teacher.id_teacher,)))
    att = Attendance.objects.filter(id_lesson=id_lesson)
    lesson = Lesson.objects.get(id=id_lesson)
    lesson.type = Type_lesson.objects.get(id=1)
    lesson.save()
    if lesson.date < Period.objects.last().date_start or lesson.date > Period.objects.last().date_end:
        return render(request, 'info/dont_create_lesson.html', {'title': 'период аттестации закончен'}, )
    for i, s in enumerate(att):
        if s.id_student.subjects.filter(subject=lesson.id_subject, group=lesson.id_group).first():
            status = Att_Status.objects.get(name='Перезачтено')
        else:
            status = Att_Status.objects.get(id=request.POST[s.id_student.id_people])
        try:
            a = Attendance.objects.get(id_student=s.id_student, id_lesson=id_lesson)
            a.status = status
            a.save()
        except Attendance.DoesNotExist:
            a = Attendance(id_student=s.id_student)
            a.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
def add_teacher(request):
    def transliterate(name):

        # Слоаврь с заменами
        slovar = {
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'е': 'e',
            'ё': 'e',
            'ж': 'zh',
            'з': 'z',
            'и': 'i',
            'й': 'i',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'ф': 'f',
            'х': 'kh',
            'ц': 'tc',
            'ч': 'ch',
            'ш': 'sh',
            'щ': 'shch',
            'ъ': '',
            'ы': 'u',
            'ь': '',
            'э': 'e',
            'ю': 'iu',
            'я': 'ia',
            'А': 'A',
            'Б': 'B',
            'В': 'V',
            'Г': 'G',
            'Д': 'D',
            'Е': 'E',
            'Ё': 'E',
            'Ж': 'ZH',
            'З': 'Z',
            'И': 'I',
            'Й': 'I',
            'К': 'K',
            'Л': 'L',
            'М': 'M',
            'Н': 'N',
            'О': 'O',
            'П': 'P',
            'Р': 'R',
            'С': 'S',
            'Т': 'T',
            'У': 'U',
            'Ф': 'F',
            'Х': 'KH',
            'Ц': 'TC',
            'Ч': 'CH',
            'Ш': 'SH',
            'Щ': 'SHCH',
            'Ъ': '',
            'Ы': 'U',
            'Ь': '',
            'Э': 'E',
            'Ю': 'IU',
            'Я': 'IA',
            '-': '',
            '_': '',
            'A': 'a',
            'B': 'b',
            'C': 'c',
            'D': 'd',
            'E': 'e',
            'F': 'f',
            'G': 'g',
            'H': 'h',
            'I': 'i',
            'J': 'j',
            'K': 'k',
            'L': 'l',
            'M': 'm',
            'N': 'n',
            'O': 'o',
            'P': 'p',
            'Q': 'q',
            'R': 'r',
            'S': 's',
            'T': 't',
            'U': 'u',
            'V': 'v',
            'W': 'w',
            'Z': 'z',
            'X': 'x',
            'Y': 'y', }

        # Циклически заменяем все буквы в строке
        for key in slovar:
            name = name.replace(key, slovar[key])
        return name

    if not request.user.is_superuser:
        return redirect("/")

    if request.method == 'POST':
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        second_name = request.POST['second_name']
        id_teacher = request.POST['id']
        username = transliterate(first_name[0].lower()) + transliterate(second_name[0].lower()) + transliterate(
            last_name.lower())
        print(username)
        # Creating a User with teacher username and password format
        # USERNAME: firstname + underscore + unique ID
        # PASSWORD: firstname + underscore + year of birth(YYYY)
        user = User.objects.create_user(
            username=transliterate(first_name[0].lower()) + transliterate(second_name[0].lower()) + transliterate(
                last_name.lower()),
            password=transliterate(first_name[0].lower()) + transliterate(second_name[0].lower()) + transliterate(
                last_name.lower()) + "@",
        )
        user.save()

        Teacher(
            user=user,
            id_teacher=id_teacher,
            last_name=last_name,
            first_name=first_name,
            second_name=second_name,
        ).save()
        return redirect('/')

    return render(request, 'info/add_teacher.html')


@login_required()
def all_att(request):
    if not request.user.is_staf:
        return redirect("/")
    form = Att_Filter_All_Form(request.GET)
    lessons = Lesson.objects.all()

    if request.method == 'GET':

        if 'group' in request.GET and request.GET['group']:
            # print(request.GET['group'])
            get_group = request.GET['group']
            lessons = lessons.filter(id_group=get_group)
        if 'subject' in request.GET and request.GET['subject']:
            get_subject = request.GET['subject']
            lessons = lessons.filter(id_subject=get_subject)
        if 'type' in request.GET and request.GET['type']:
            get_type = request.GET['type']
            lessons = lessons.filter(type=get_type)
        if 'teacher' in request.GET and request.GET['teacher']:
            get_teacher = request.GET['teacher']
            lessons = lessons.filter(id_teacher=get_teacher)
        if 'period' in request.GET and request.GET['period']:
            period = request.GET['period']
            lessons = lessons.filter(period=period)
        if 'end_date' in request.GET and request.GET['end_date'] and not request.GET['start_date']:
            get_end_date = (request.GET['end_date'])
            lessons = lessons.filter(date__lte=get_end_date)
        if 'start_date' in request.GET and request.GET['start_date']:
            get_start_date = (request.GET['start_date'])
            lessons = lessons.filter(date__gte=get_start_date)
            if 'end_date' in request.GET and request.GET['end_date']:
                get_end_date = (request.GET['end_date'])
                lessons = lessons.filter(date__range=(get_start_date, get_end_date))

    att = {}
    for lesson in lessons:
        out = Attendance.objects.filter(id_lesson=lesson.id, status=0)
        present = Attendance.objects.filter(id_lesson=lesson.id, status=1)
        late = Attendance.objects.filter(id_lesson=lesson.id, status=2)
        half = Attendance.objects.filter(id_lesson=lesson.id, status=3)

        att.update({
            lesson.id: {
                'out': len(out),
                'present': len(present),
                'late': len(late),
                'half': len(half),
            }})
    group_and_subjects = []
    for lesson in lessons:
        group_and_subject = Group_and_Subject.objects.filter(subject=lesson.id_subject, group=lesson.id_group)
        group_and_subjects.append(group_and_subject)

    context = {
        'lesson_list': lessons,
        'atts': att,
        'form': form,
        'group_and_subject': group_and_subjects,

    }
    return render(request, 'info/all_att.html', context=context)


@login_required()
def t_subjects(request, get_object_or_404):
    if not request.user.is_teacher:
        return redirect("/")

    form = Subjects_Filter_Form(request.GET, request=request)
    period = Period.objects.last()
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    get_group = ''
    students = ''
    if request.method == 'GET':
        # if 'teacher' in request.GET and request.GET['teacher']:
        # get_teacher = get_object_or_404(Teacher, id=request.GET['teacher']).id_teacher
        if 'period' in request.GET and request.GET['period']:
            period = get_object_or_404(Period, id=request.GET['period'])
            get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
            get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
            date = get_period_start
        if 'group_and_subject' in request.GET and request.GET['group_and_subject']:
            get_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group.id_group_rasp
            get_group_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group
            get_subject = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).subject.name

            students = Group_Contingent.objects.get(id_group_rasp=get_group, period=period).students.filter(
                expelled=False).order_by('last_name')
            print(students)
            # Student.objects.filter(id_group=get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group, expelled=False)

        if 'type' in request.GET and request.GET['type']:
            get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
        while date < get_period_end:
            rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={get_group}&date={date}', verify=False)

            for k in rp.json()['data']:
                date_lesson = ("-").join(k['date'].split('.')[::-1])
                if Holyday.objects.filter(date=date_lesson).exists():
                    continue
                # format = '%Y-%m-%d'
                # date_lesson = datetime.datetime.strptime(date_less, format)
                if "href" in k['subject']:
                    subject = k['subject'].split('>')[1].split('<')[0]
                else:
                    subject = k['subject']
                if subject == get_subject:
                    for teach in k['teachers']:
                        if teach['id'] == request.user.teacher.id_teacher:
                            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                                if Attendance.objects.filter(id_lesson=id_lesson):
                                    if len(Attendance.objects.filter(id_lesson=id_lesson)) != len(students):
                                        for stud in students:
                                            # print(stud,stud.id)
                                            if Attendance.objects.filter(id_lesson=id_lesson,
                                                                         id_student__id_group=get_group_group,
                                                                         id_student__expelled=False,
                                                                         id_student=stud.id).exists():
                                                print(stud, Attendance.objects.get(id_lesson=id_lesson,
                                                                                   id_student__id_group=get_group_group,
                                                                                   id_student__expelled=False,
                                                                                   id_student=stud.id))
                                                student_atts.append(Attendance.objects.get(id_lesson=id_lesson,
                                                                                           id_student__id_group=get_group_group,
                                                                                           id_student__expelled=False,
                                                                                           id_student=stud.id))
                                            else:
                                                student_atts.append('-')
                                    else:
                                        # print(Attendance.objects.filter(id_lesson=id_lesson, id_student__expelled=False))
                                        student_atts = (Attendance.objects.filter(id_lesson=id_lesson,
                                                                                  id_student__expelled=False).order_by(
                                            'id_student'))
                                    # print(type(student_atts),student_atts, get_group)
                                else:
                                    # print('nety att')
                                    student_atts = [0 for j in range(len(students))]
                            else:
                                # print('nety lesson')
                                student_atts = [0 for j in range(len(students))]
                            if request.GET['type']:
                                if get_type == (k['type']) and (k['cancel']) != '0':
                                    lessons_name.append({
                                        'subject': subject,
                                        'group': get_object_or_404(Group_and_Subject,
                                                                   id=request.GET['group_and_subject']).group,
                                        'weekday': k['weekday'],
                                        'date': date_lesson,
                                        'id': k['id'].split(',')[0],
                                        'para': k['para'],
                                        'type': type_lessons[int(k['type'])],
                                        'cancel': k['cancel'],
                                        'student_atts': student_atts,
                                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                                     date=date_lesson).status if Lesson.objects.filter(
                                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                        'date2': k['date'],
                                        'id_lesson': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                                        date=date_lesson).id if Lesson.objects.filter(
                                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                    })
                            else:
                                if not int(k['type']) > 2 and (k['cancel']) != '0':
                                    lessons_name.append({
                                        'subject': subject,
                                        'group': get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group,
                                        'weekday': k['weekday'],
                                        'date': date_lesson,
                                        'id': k['id'].split(',')[0],
                                        'para': k['para'],
                                        'type': type_lessons[int(k['type'])],
                                        'cancel': k['cancel'],
                                        'student_atts': student_atts,
                                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                                     date=date_lesson).status if Lesson.objects.filter(
                                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                        'date2': k['date'],
                                        'id_lesson': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                                        date=date_lesson).id if Lesson.objects.filter(
                                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                    })
                            # print(lessons_name)
                            student_atts = []

            date = (date + datetime.timedelta(days=7))

    class_matrix = [[i for i in range(len(lessons_name) + 3)] for j in range(len(students))]
    # print(type(start_week))
    format = '%Y-%m-%d'
    for i, d in enumerate(students):
        # print(i, d)
        for j in range(len(lessons_name) + 3):
            # print(type(lessons_name[j-2]))
            if j == 0:
                # print(i)
                class_matrix[i][0] = i + 1

            elif j == 1:
                class_matrix[i][1] = d
            elif j == 2:
                class_matrix[i][2] = ''

            else:
                for k in range(len(lessons_name[j - 3]['student_atts'])):
                    if lessons_name[j - 3]['student_atts'][k] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name[j - 3]['student_atts'][k] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        # print(lessons_name[j-3]['student_atts'][k].status.short_name)
                        class_matrix[k][j] = lessons_name[j - 3]['student_atts'][k].status.short_name

    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0

    for i, d in enumerate(class_matrix):
        for j, att in enumerate(d):
            if j > 2:
                if att != '':
                    count += 1
                if att == 'П':
                    count_p += 1
                if att == 'Н':
                    count_n += 1
                if att == 'О':
                    count_o += 1
                if att == 'ЧП':
                    count_ch += 1
        class_matrix[i][2] = f'{j - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0

    context = {
        'time_slots': class_matrix,
        'lessons_name': lessons_name,
        'students': students,
        'date': date,
        'form': form,
        'group': get_group,
        'period': period.id,

    }
    return render(request, 'info/t_subjects.html', context=context)


@login_required()
def all_subjects(request):
    if not request.user.is_staf:
        return redirect("/")
    form = Subjects_Filter_All_Form(request.GET)
    period = Period.objects.last()
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    get_group = ''
    students = ''
    teachers = []

    if request.method == 'GET':
        # if 'teacher' in request.GET and request.GET['teacher']:
        # get_teacher = get_object_or_404(Teacher, id=request.GET['teacher']).id_teacher
        if 'period' in request.GET and request.GET['period']:
            period = get_object_or_404(Period, id=request.GET['period'])
            get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
            get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
            date = get_period_start
        if 'group_and_subject' in request.GET and request.GET['group_and_subject']:
            get_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group.id_group_rasp
            get_group_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group
            # print(get_group)
            get_subject = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).subject.name
            # print(get_subject)
            students = Student.objects.filter(
                id_group=get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group,
                expelled=False)
            # print(students)
        # if 'teacher' in request.GET and request.GET['teacher']:
        # get_teacher = get_object_or_404(Teacher, id=request.GET['teacher']).id_teacher
        if 'type' in request.GET and request.GET['type']:
            get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
        while date < get_period_end:
            rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={get_group}&date={date}', verify=False)

            for k in rp.json()['data']:
                date_lesson = ("-").join(k['date'].split('.')[::-1])
                if Holyday.objects.filter(date=date_lesson).exists():
                    continue
                # format = '%Y-%m-%d'
                # date_lesson = datetime.datetime.strptime(date_less, format)
                if "href" in k['subject']:
                    subject = k['subject'].split('>')[1].split('<')[0]
                else:
                    subject = k['subject']

                if subject == get_subject:
                    for teach in k['teachers']:
                        teachers.append(teach['fio'].replace('&nbsp;', ' '))
                    if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                        id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                        # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                        if Attendance.objects.filter(id_lesson=id_lesson):
                            if len(Attendance.objects.filter(id_lesson=id_lesson)) != len(students):
                                for stud in students:
                                    print(stud, stud.id)
                                    if Attendance.objects.filter(id_lesson=id_lesson,
                                                                 id_student__id_group=get_group_group,
                                                                 id_student__expelled=False,
                                                                 id_student=stud.id).exists():
                                        student_atts.append(Attendance.objects.get(id_lesson=id_lesson,
                                                                                   id_student__id_group=get_group_group,
                                                                                   id_student__expelled=False,
                                                                                   id_student=stud.id))
                                    else:
                                        student_atts.append('-')
                            else:
                                student_atts = (
                                    Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                              id_student__expelled=False)).order_by('id_student')
                            # print(student_atts)
                        else:
                            # print('nety att')
                            student_atts = [0 for j in range(len(students))]
                    else:
                        # print('nety lesson')
                        student_atts = [0 for j in range(len(students))]
                    if request.GET['type']:
                        if get_type == (k['type']) and (k['cancel']) != '0':
                            lessons_name.append({
                                'subject': subject,
                                'group': get_object_or_404(Group_and_Subject,
                                                           id=request.GET['group_and_subject']).group,
                                'weekday': k['weekday'],
                                'date': date_lesson,
                                'id': k['id'].split(',')[0],
                                'para': k['para'],
                                'type': type_lessons[int(k['type'])],
                                'cancel': k['cancel'],
                                'student_atts': student_atts,
                                'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                             date=date_lesson).status if Lesson.objects.filter(
                                    id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                'date2': k['date'],
                                'teachers': teachers,
                            })
                    else:
                        if not int(k['type']) > 2 and (k['cancel']) != '0':
                            lessons_name.append({
                                'subject': subject,
                                'group': get_object_or_404(Group_and_Subject,
                                                           id=request.GET['group_and_subject']).group,
                                'weekday': k['weekday'],
                                'date': date_lesson,
                                'id': k['id'].split(',')[0],
                                'para': k['para'],
                                'type': type_lessons[int(k['type'])],
                                'cancel': k['cancel'],
                                'student_atts': student_atts,
                                'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                             date=date_lesson).status if Lesson.objects.filter(
                                    id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                                'date2': k['date'],
                                'teachers': teachers,
                            })

                    student_atts = []
                    teachers = []
            date = (date + datetime.timedelta(days=7))

    class_matrix = [[i for i in range(len(lessons_name) + 3)] for j in range(len(students))]
    # print(type(start_week))
    format = '%Y-%m-%d'
    for i, d in enumerate(students):
        # print(i, d)
        for j in range(len(lessons_name) + 3):

            if j == 0:
                # print(i)
                class_matrix[i][0] = i + 1

            elif j == 1:
                class_matrix[i][1] = d
            elif j == 2:
                class_matrix[i][2] = ''

            else:
                for k in range(len(lessons_name[j - 3]['student_atts'])):
                    if lessons_name[j - 3]['student_atts'][k] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name[j - 3]['student_atts'][k] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        # print(att_status['1'])
                        class_matrix[k][j] = lessons_name[j - 3]['student_atts'][k].status.short_name

    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0

    for i, d in enumerate(class_matrix):
        for j, att in enumerate(d):
            if j > 2:
                if att != '':
                    count += 1
                if att == 'П':
                    count_p += 1
                if att == 'Н':
                    count_n += 1
                if att == 'О':
                    count_o += 1
                if att == 'ЧП':
                    count_ch += 1
        class_matrix[i][2] = f'{j - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0

    context = {
        'time_slots': class_matrix,
        'lessons_name': lessons_name,
        'students': students,
        'date': date,
        'form': form,
        'group': get_group,
        'period': period.id,

    }
    return render(request, 'info/all_subjects.html', context=context)


@login_required()
def t_subjects2(request):
    if not request.user.is_teacher:
        return redirect("/")
    form = Subjects_Filter_Form(request.GET)
    period = Period.objects.last()
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_student = ''
    get_lessons = ''
    students = ''
    groupid = ''
    get_att = ''
    if request.method == 'GET':
        if 'group_and_subject' in request.GET and request.GET['group_and_subject']:
            get_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group.id_group_rasp
            get_group_group = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group
            # print(get_group)
            get_subject = get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).subject.name
            # print(get_subject)
            students = Student.objects.filter(
                id_group=get_object_or_404(Group_and_Subject, id=request.GET['group_and_subject']).group,
                expelled=False)
            # print(students)
        if 'period' in request.GET and request.GET['period']:
            get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
            get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
            date = get_period_start
        if 'type' in request.GET and request.GET['type']:
            get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    while date < get_period_end:

        rp = requests.get(
            f'http://raspisanie.ssti.ru/data.php?teacher_week={request.user.teacher.id_teacher}&date={date}',
            verify=False)

        for k in rp.json()['data']:
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']

            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Attendance.objects.filter(id_lesson=id_lesson):
                    if len(Attendance.objects.filter(id_lesson=id_lesson)) != len(students):
                        for stud in students:
                            # print(stud,stud.id)
                            if Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                         id_student__expelled=False, id_student=stud.id).exists():
                                student_atts.append(
                                    Attendance.objects.get(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                           id_student__expelled=False, id_student=stud.id))
                            else:
                                student_atts.append('-')
                    else:
                        student_atts = (
                            Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                      id_student__expelled=False))
                    # print(student_atts)
                else:
                    # print('nety att')
                    student_atts = [0 for j in range(len(students))]
            else:
                # print('nety lesson')
                student_atts = [0 for j in range(len(students))]
            if 'type' in request.GET and request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': k['id_group'],
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': k['id_group'],
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                    })

            name_subject = subject

            if len(lessons_name) <= 0:
                continue
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})
            student_atts = []
            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    print(lessons_name_subject)

    class_matrix = [[i for i in range(len(lessons_name) + 3)] for j in range(len(students))]
    # print(type(start_week))
    format = '%Y-%m-%d'
    for i, d in enumerate(students):
        # print(i, d)
        for j in range(len(lessons_name) + 3):

            if j == 0:
                # print(i)
                class_matrix[i][0] = i + 1

            elif j == 1:
                class_matrix[i][1] = d
            elif j == 2:
                class_matrix[i][2] = ''

            else:
                for k in range(len(lessons_name[j - 3]['student_atts'])):
                    if lessons_name[j - 3]['student_atts'][k] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name[j - 3]['student_atts'][k] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        # print(att_status['1'])
                        class_matrix[k][j] = lessons_name[j - 3]['student_atts'][k].status.short_name

    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0

    for i, d in enumerate(class_matrix):
        for j, att in enumerate(d):
            if j > 2:
                if att != '':
                    count += 1
                if att == 'П':
                    count_p += 1
                if att == 'Н':
                    count_n += 1
                if att == 'О':
                    count_o += 1
                if att == 'ЧП':
                    count_ch += 1
        class_matrix[i][2] = f'{j - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0

    context = {
        'time_slots': class_matrix,
        'lessons_name': lessons_name,
        'students': students,
        'date': date,
        'form': form,
        'group': get_group,
        'period': period.id,

    }
    return render(request, 'info/t_subjects2.html', context=context)


@login_required()
def all_stat(request):
    if not request.user.is_staf:
        return redirect("/")
    form = All_Stat(request.GET)
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_student = ''
    get_lessons = ''
    students = ''
    groupid = ''
    get_att = ''
    teachers = []
    if 'student' in request.GET and request.GET['student']:
        get_student = get_object_or_404(Student, id=request.GET['student'])
        get_lessons = Lesson.objects.filter(id_group=get_student.id_group)
        get_att = Attendance.objects.filter(id_student=get_student)
        groupid = get_student.id_group.id_group_rasp
    if 'period' in request.GET and request.GET['period']:
        get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
        get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
        date = get_period_start
    if 'type' in request.GET and request.GET['type']:
        get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    while date < get_period_end:

        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={groupid}&date={date}', verify=False)

        for k in rp.json()['data']:
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']
            for teach in k['teachers']:
                teachers.append(teach['fio'].replace('&nbsp;', ' '))
            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).status == True:
                    if Attendance.objects.filter(id_lesson=id_lesson, id_student=get_student):
                        student_atts = (Attendance.objects.get(id_lesson=id_lesson, id_student=get_student))
                    else:
                        student_atts = '-'
                else:
                    # print('nety att')
                    student_atts = 0
            else:
                # print('nety lesson')
                student_atts = 0
            if request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,
                    })

            name_subject = subject
            teachers = []
            student_atts = []
            if len(lessons_name) <= 0:
                continue
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})

            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    # print(lessons_name_subject['Программирование микропроцессорных систем'])

    format = '%Y-%m-%d'
    class_matrix_subjects = {}
    for item in lessons_name_subject:
        # print(lessons_name_subject[item][0]['group'])

        class_matrix = [[i for i in range(len(lessons_name_subject[item]) + 3)] for j in range(1)]
        # print(len(lessons_name_subject[item])+2)

        for j in range(len(lessons_name_subject[item]) + 3):
            # print((lessons_name_subject[item]))
            # print(lessons_name_subject[item][j-2]['student_atts'])
            if j == 0:
                # print(i)
                class_matrix[0][0] = 0 + 1

            elif j == 1:
                class_matrix[0][1] = get_student
            elif j == 2:
                class_matrix[0][2] = ""

            else:
                for k in range(1):

                    if lessons_name_subject[item][j - 3]['student_atts'] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name_subject[item][j - 3]['student_atts'] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        # print(lessons_name_subject[item][j-2]['student_atts'][k].status, lessons_name_subject[item][j-2]['group'])
                        # print(k, (lessons_name_subject[item][j-2]['student_atts'][k]))
                        # print(lessons_name_subject[item][j-2]['student_atts'])
                        class_matrix[k][j] = lessons_name_subject[item][j - 3]['student_atts'].status.short_name

            class_matrix_subjects.update({item: class_matrix})
    # print((class_matrix_subjects['Программирование микропроцессорных систем'][0]))
    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0
    count_subjects = {}
    for item in class_matrix_subjects:
        for i, d in enumerate(class_matrix_subjects[item][0]):
            if i > 2:
                if d != '':
                    count += 1
                if d == 'П':
                    count_p += 1
                if d == 'Н':
                    count_n += 1
                if d == 'О':
                    count_o += 1
                if d == 'ЧП':
                    count_ch += 1
            class_matrix_subjects[item][0][2] = f'{i - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'
        # print(count)
        count_subjects.update({item: count})
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0

    context = {
        'student': get_student,
        'lessons': get_lessons,
        'count_subjects': count_subjects,
        'atts': get_att,
        'date': date,
        'form': form,
        'group': get_group,
        'time_slots': class_matrix_subjects,
        'lessons_name': lessons_name_subject,
    }
    return render(request, 'info/all_stat.html', context=context)


@login_required()
def all_stat_group(request):
    if not request.user.is_staf:
        return redirect("/")
    form = All_Stat_Group(request.GET)
    period = Period.objects.last()
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_lessons = ''
    students = ''
    groupid = ''
    get_att = ''
    teachers = []
    if 'group' in request.GET and request.GET['group']:
        get_group = get_object_or_404(Group_Contingent, id=request.GET['group']).id_group_rasp
        get_group_group = get_object_or_404(Group_Contingent, id=request.GET['group'])
        students = Student.objects.filter(id_group=get_object_or_404(Group_Contingent, id=request.GET['group']),
                                          expelled=False)
        # print(students)
    if 'period' in request.GET and request.GET['period']:
        get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
        get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
        date = get_period_start
    if 'type' in request.GET and request.GET['type']:
        get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    while date < get_period_end:

        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={get_group}&date={date}', verify=False)

        for k in rp.json()['data']:
            # print(k)
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']
            for teach in k['teachers']:
                teachers.append(teach['fio'].replace('&nbsp;', ' '))

            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Attendance.objects.filter(id_lesson=id_lesson):
                    if len(Attendance.objects.filter(id_lesson=id_lesson)) != len(students):
                        for stud in students:
                            # print(stud,stud.id)
                            if Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                         id_student__expelled=False, id_student=stud.id).exists():
                                student_atts.append(
                                    Attendance.objects.get(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                           id_student__expelled=False, id_student=stud.id))

                            else:
                                student_atts.append('-')
                    else:
                        student_atts = (
                            Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                      id_student__expelled=False)).order_by('id_student')
                    # print(student_atts)
                else:
                    # print('nety att')
                    student_atts = [0 for j in range(len(students))]
            else:
                # print('nety lesson')
                student_atts = [0 for j in range(len(students))]
            # print(Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson), student_atts)
            if request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_group_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_group_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,
                    })

            name_subject = subject
            student_atts = []
            teachers = []
            if len(lessons_name) <= 0:
                continue
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})

            # print(student_atts)
            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    format = '%Y-%m-%d'
    class_matrix_subjects = {}
    for item in lessons_name_subject:
        # print(lessons_name_subject[item][0]['group'])

        class_matrix = [[i for i in range(len(lessons_name_subject[item]) + 3)] for j in range(len(students))]
        # print(len(lessons_name_subject[item])+2)
        for i, d in enumerate(students):
            for j in range(len(lessons_name_subject[item]) + 3):
                # print((lessons_name_subject[item]))
                # print(lessons_name_subject[item][j-2]['student_atts'])
                # print(lessons_name_subject[item][j-3]['student_atts'])
                if j == 0:
                    # print(i)
                    class_matrix[i][0] = i + 1

                elif j == 1:
                    class_matrix[i][1] = d
                elif j == 2:
                    class_matrix[i][2] = ""

                else:
                    for k in range(len(lessons_name_subject[item][j - 3]['student_atts'])):
                        # print(k)
                        if lessons_name_subject[item][j - 3]['student_atts'][k] == 0:
                            class_matrix[k][j] = ''
                        elif lessons_name_subject[item][j - 3]['student_atts'][k] == '-':
                            class_matrix[k][j] = '-'
                        else:
                            # print(lessons_name_subject[item][j-2]['student_atts'][k].status, lessons_name_subject[item][j-2]['group'])
                            # print(k, (lessons_name_subject[item][j-3]['student_atts'][k].status.short_name))
                            # print(lessons_name_subject[item][j-3]['student_atts'][k], k)

                            class_matrix[k][j] = lessons_name_subject[item][j - 3]['student_atts'][k].status.short_name

                class_matrix_subjects.update({item: class_matrix})
    # print((class_matrix_subjects['Программирование микропроцессорных систем'][0]))
    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0
    count_subjects = {}
    for item in class_matrix_subjects:
        for i, d in enumerate(class_matrix_subjects[item]):
            for j, att in enumerate(d):

                if j > 2:

                    if att != '':
                        count += 1
                    if att == 'П':
                        count_p += 1
                    if att == 'Н':
                        count_n += 1
                    if att == 'О':
                        count_o += 1
                    if att == 'ЧП':
                        count_ch += 1
            class_matrix_subjects[item][i][2] = f'{j - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'

            count_subjects.update({item: count})
            count = 0
            count_p = 0
            count_n = 0
            count_o = 0
            count_ch = 0

    context = {
        'time_slots': class_matrix_subjects,
        'lessons_name': lessons_name_subject,
        'students': students,
        'date': date,
        'form': form,
        'group': get_group,
        'period': period.id,
        'count_subjects': count_subjects,

    }
    return render(request, 'info/all_stat_group.html', context=context)


@login_required()
def t_stat_group(request):
    if not request.user.is_teacher:
        return redirect("/")
    form = Stat_Group(request.GET, request=request)
    period = Period.objects.last()
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_lessons = ''
    students = ''
    groupid = ''
    get_att = ''
    teachers = []
    teacher_fio = f'{request.user.teacher.last_name} {request.user.teacher.first_name[0]}.{request.user.teacher.second_name[0]}.'
    if 'group' in request.GET and request.GET['group']:
        get_group = get_object_or_404(Group_Contingent, id=request.GET['group']).id_group_rasp
        get_group_group = get_object_or_404(Group_Contingent, id=request.GET['group'])
        # students = Student.objects.filter(id_group=get_object_or_404(Group_Contingent, id=request.GET['group']), expelled=False)
        students = get_object_or_404(Group_Contingent, id=request.GET['group']).students.all()
    if 'period' in request.GET and request.GET['period']:
        get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
        get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
        date = get_period_start
    if 'type' in request.GET and request.GET['type']:
        get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    while date < get_period_end:

        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={get_group}&date={date}', verify=False)

        for k in rp.json()['data']:
            teachers = []
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']

            for teach in k['teachers']:
                teachers.append(teach['fio'].replace('&nbsp;', ' '))
            # print(teacher_fio, teachers)
            if teacher_fio not in teachers:
                continue
            if Subject.objects.filter(name=subject).first() not in request.user.teacher.subjects.all():
                continue
            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Attendance.objects.filter(id_lesson=id_lesson):
                    if len(Attendance.objects.filter(id_lesson=id_lesson)) != len(students):
                        for stud in students:
                            # print(stud,stud.id)
                            if Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                         id_student__expelled=False, id_student=stud.id).exists():
                                student_atts.append(
                                    Attendance.objects.get(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                           id_student__expelled=False, id_student=stud.id))

                            else:
                                student_atts.append('-')
                    else:
                        student_atts = (
                            Attendance.objects.filter(id_lesson=id_lesson, id_student__id_group=get_group_group,
                                                      id_student__expelled=False)).order_by('id_student')
                    # print(student_atts)
                else:
                    # print('nety att')
                    student_atts = [0 for j in range(len(students))]
            else:
                # print('nety lesson')
                student_atts = [0 for j in range(len(students))]
            # print(student_atts)
            if request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_group_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_group_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,
                    })

            name_subject = subject
            teachers = []
            student_atts = []
            # print(lessons_name)
            if len(lessons_name) <= 0:
                continue
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})

            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    # print(lessons_name_subject)
    format = '%Y-%m-%d'
    class_matrix_subjects = {}
    for item in lessons_name_subject:
        # print(lessons_name_subject[item][0])

        class_matrix = [[i for i in range(len(lessons_name_subject[item]) + 3)] for j in range(len(students))]
        # print(len(lessons_name_subject[item])+2)
        for i, d in enumerate(students):
            # print(students)
            for j in range(len(lessons_name_subject[item]) + 3):
                # print((lessons_name_subject[item]))
                # print(lessons_name_subject[item][j-2]['student_atts'])
                # print(lessons_name_subject[item][j-3]['student_atts'])
                if j == 0:
                    # print(i)
                    class_matrix[i][0] = i + 1

                elif j == 1:
                    class_matrix[i][1] = d
                elif j == 2:
                    class_matrix[i][2] = ""

                else:
                    for k in range(len(lessons_name_subject[item][j - 3]['student_atts'])):
                        # print(k)
                        if lessons_name_subject[item][j - 3]['student_atts'][k] == 0:
                            class_matrix[k][j] = ''
                        elif lessons_name_subject[item][j - 3]['student_atts'][k] == '-':
                            class_matrix[k][j] = '-'
                        else:
                            # print(lessons_name_subject[item][j-2]['student_atts'][k].status, lessons_name_subject[item][j-2]['group'])
                            # print(k, (lessons_name_subject[item][j-2]['student_atts'][k]))
                            # print(lessons_name_subject[item][j-3]['student_atts'], k)
                            class_matrix[k][j] = lessons_name_subject[item][j - 3]['student_atts'][k].status.short_name
                # print(class_matrix)
                class_matrix_subjects.update({item: class_matrix})
    # print((class_matrix_subjects))
    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0
    count_subjects = {}
    for item in class_matrix_subjects:
        for i, d in enumerate(class_matrix_subjects[item]):
            for j, att in enumerate(d):

                if j > 2:

                    if att != '':
                        count += 1
                    if att == 'П':
                        count_p += 1
                    if att == 'Н':
                        count_n += 1
                    if att == 'О':
                        count_o += 1
                    if att == 'ЧП':
                        count_ch += 1
            class_matrix_subjects[item][i][2] = f'{j - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'

            count_subjects.update({item: count})
            count = 0
            count_p = 0
            count_n = 0
            count_o = 0
            count_ch = 0

    context = {
        'time_slots': class_matrix_subjects,
        'lessons_name': lessons_name_subject,
        'students': students,
        'date': date,
        'form': form,
        'group': get_group,
        'period': period.id,
        'count_subjects': count_subjects,

    }
    return render(request, 'info/t_stat_group.html', context=context)


@login_required()
def t_stat_student(request):
    if not request.user.is_teacher:
        return redirect("/")
    form = All_Stat(request.GET)
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_student = ''
    get_lessons = ''
    students = ''
    groupid = ''
    get_att = ''
    teachers = []
    if 'student' in request.GET and request.GET['student']:
        get_student = get_object_or_404(Student, id=request.GET['student'])
        # get_lessons = Lesson.objects.filter(id_group=get_student.id_group)
        get_att = Attendance.objects.filter(id_student=get_student)
        groupid = get_student.id_group.id_group_rasp
    if 'period' in request.GET and request.GET['period']:
        get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
        get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
        date = get_period_start
    if 'type' in request.GET and request.GET['type']:
        get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    while date < get_period_end:

        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={groupid}&date={date}', verify=False)

        for k in rp.json()['data']:
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']

            if not request.user.teacher.group_and_subjects.all().filter(subject__name=subject,
                                                                        group__id_group_rasp=groupid).exists():
                continue
            else:
                for teach in k['teachers']:
                    teachers.append(teach['fio'].replace('&nbsp;', ' '))
            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).status == True:
                    if Attendance.objects.filter(id_lesson=id_lesson, id_student=get_student):
                        student_atts = (Attendance.objects.get(id_lesson=id_lesson, id_student=get_student))
                    else:
                        student_atts = '-'
                else:
                    # print('nety att')
                    student_atts = 0
            else:
                # print('nety lesson')
                student_atts = 0
            if request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                        'teachers': teachers,
                    })

            name_subject = subject
            teachers = []
            student_atts = []
            if len(lessons_name) <= 0:
                continue
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})

            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    # print(lessons_name_subject['Программирование микропроцессорных систем'])

    format = '%Y-%m-%d'
    class_matrix_subjects = {}
    for item in lessons_name_subject:
        # print(lessons_name_subject[item][0]['group'])

        class_matrix = [[i for i in range(len(lessons_name_subject[item]) + 3)] for j in range(1)]
        # print(len(lessons_name_subject[item])+2)

        for j in range(len(lessons_name_subject[item]) + 3):
            # print((lessons_name_subject[item]))
            # print(lessons_name_subject[item][j-2]['student_atts'])
            if j == 0:
                # print(i)
                class_matrix[0][0] = 0 + 1

            elif j == 1:
                class_matrix[0][1] = get_student
            elif j == 2:
                class_matrix[0][2] = ''

            else:
                for k in range(1):

                    if lessons_name_subject[item][j - 3]['student_atts'] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name_subject[item][j - 3]['student_atts'] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        class_matrix[k][j] = lessons_name_subject[item][j - 3]['student_atts'].status.short_name

            class_matrix_subjects.update({item: class_matrix})
    # print((class_matrix_subjects['Программирование микропроцессорных систем'][0]))
    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0
    count_subjects = {}
    for item in class_matrix_subjects:
        for i, d in enumerate(class_matrix_subjects[item][0]):
            if i > 2:
                if d != '':
                    count += 1
                if d == 'П':
                    count_p += 1
                if d == 'Н':
                    count_n += 1
                if d == 'О':
                    count_o += 1
                if d == 'ЧП':
                    count_ch += 1
            class_matrix_subjects[item][0][2] = f'{i - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'
        # print(count)
        count_subjects.update({item: count})
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0
    context = {
        'student': get_student,
        # 'lessons':get_lessons,
        'count_subjects': count_subjects,
        'atts': get_att,
        'date': date,
        'form': form,
        'group': get_group,
        'time_slots': class_matrix_subjects,
        'lessons_name': lessons_name_subject,
    }
    return render(request, 'info/t_stat_student.html', context=context)


@login_required()
def s_stat(request):
    # проверка, что авторизированный пользователь студент
    if not request.user.is_student:
        return redirect("/")
    form = S_Stat(request.GET)
    get_period_start = Period.objects.last().date_start
    get_period_end = Period.objects.last().date_end
    date = get_period_start
    lessons_name = []
    student_atts = []
    lessons_name_subject = {}
    get_group = ''
    get_student = request.user.student  # получаем мета класс студента авторизированного пользователя
    get_lessons = ''

    groupid = get_student.id_group.id_group_rasp  # получаем ID группы в расписании студента
    get_att = ''
    # проверка на заполнение полей формы
    if 'period' in request.GET and request.GET['period']:
        get_period_start = get_object_or_404(Period, id=request.GET['period']).date_start
        get_period_end = get_object_or_404(Period, id=request.GET['period']).date_end
        date = get_period_start
    if 'type' in request.GET and request.GET['type']:
        get_type = get_object_or_404(Type_lesson, id=request.GET['type']).id_type
    # цикл, который проходит по расписанию начиная с даты начала выбранного периода в форме, если не выбран период, то берется последний
    while date < get_period_end:

        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={groupid}&date={date}', verify=False)
        # цикл, который проходит по занятиям из расписания на неделе
        for k in rp.json()['data']:
            date_lesson = ("-").join(k['date'].split('.')[::-1])
            if Holyday.objects.filter(date=date_lesson).exists():
                continue
            # format = '%Y-%m-%d'
            # date_lesson = datetime.datetime.strptime(date_less, format)
            if "href" in k['subject']:
                subject = k['subject'].split('>')[1].split('<')[0]
            else:
                subject = k['subject']

            if Lesson.objects.filter(id_lesson=k['id'].split(',')[0], date=date_lesson):
                id_lesson = Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id
                # print('est yrok', Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).id)
                if Lesson.objects.get(id_lesson=k['id'].split(',')[0], date=date_lesson).status == True:
                    if Attendance.objects.filter(id_lesson=id_lesson, id_student=get_student):
                        student_atts = (Attendance.objects.get(id_lesson=id_lesson, id_student=get_student))
                    else:
                        student_atts = '-'
                else:
                    # print('nety att')
                    student_atts = 0
            else:
                # print('nety lesson')
                student_atts = 0
            # условие для фильтрации занятий, если в форме выбран тип занятия

            if 'type' in request.GET and request.GET['type']:
                if get_type == (k['type']) and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],

                    })
            else:
                if not int(k['type']) > 2 and (k['cancel']) != '0':
                    lessons_name.append({
                        'subject': subject,
                        'group': get_student.id_group,
                        'weekday': k['weekday'],
                        'date': date_lesson,
                        'id': k['id'].split(',')[0],
                        'para': k['para'],
                        'type': type_lessons[int(k['type'])],
                        'cancel': k['cancel'],
                        'student_atts': student_atts,
                        'status': Lesson.objects.get(id_lesson=k['id'].split(',')[0],
                                                     date=date_lesson).status if Lesson.objects.filter(
                            id_lesson=k['id'].split(',')[0], date=date_lesson).exists() else '0',
                        'date2': k['date'],
                    })

            name_subject = subject

            if len(lessons_name) <= 0:
                continue
            # формирования словаря: ключ - название предмета, данные - список занятий
            if name_subject in lessons_name_subject.keys():
                lessons_name_subject.update({name_subject: lessons_name_subject[name_subject] + lessons_name})
            else:
                lessons_name_subject.update({name_subject: lessons_name})
            student_atts = []
            lessons_name = []

        date = (date + datetime.timedelta(days=7))

    format = '%Y-%m-%d'
    # формирование таблицы для отображения посещаемости
    class_matrix_subjects = {}
    # проходим по словарю с предметами
    for item in lessons_name_subject:

        # создаем пустую матрицу исходя из количества занятий по данному предмету
        class_matrix = [[i for i in range(len(lessons_name_subject[item]) + 3)] for j in range(1)]

        # проходим по каждому занятию и заносим данные в матрицу
        for j in range(len(lessons_name_subject[item]) + 3):

            if j == 0:

                class_matrix[0][0] = 0 + 1

            elif j == 1:
                class_matrix[0][1] = get_student
            elif j == 2:
                class_matrix[0][2] = ''

            else:
                for k in range(1):

                    if lessons_name_subject[item][j - 3]['student_atts'] == 0:
                        class_matrix[k][j] = ''
                    elif lessons_name_subject[item][j - 3]['student_atts'] == '-':
                        class_matrix[k][j] = '-'
                    else:
                        class_matrix[k][j] = lessons_name_subject[item][j - 3]['student_atts'].status.short_name

            class_matrix_subjects.update({item: class_matrix})
    # считаем количество типов посещений
    count = 0
    count_p = 0
    count_n = 0
    count_o = 0
    count_ch = 0
    count_subjects = {}
    for item in class_matrix_subjects:
        for i, d in enumerate(class_matrix_subjects[item][0]):
            if i > 2:
                if d != '':
                    count += 1
                if d == 'П':
                    count_p += 1
                if d == 'Н':
                    count_n += 1
                if d == 'О':
                    count_o += 1
                if d == 'ЧП':
                    count_ch += 1
            class_matrix_subjects[item][0][2] = f'{i - 2}/{count_p}/{count_n}/{count_o}/{count_ch}'

        count_subjects.update({item: count})
        count = 0
        count_p = 0
        count_n = 0
        count_o = 0
        count_ch = 0
    # формируем словарь для передачи в шаблон
    context = {
        'student': get_student,
        # 'lessons':get_lessons,
        'count_subjects': count_subjects,
        'atts': get_att,
        'date': date,
        'form': form,
        'group': get_group,
        'time_slots': class_matrix_subjects,
        'lessons_name': lessons_name_subject,
    }
    return render(request, 'info/s_stat.html', context=context)


@login_required()
def list_group(request):
    if not request.user.is_teacher and not request.user.is_staf:
        return redirect("/")

    form = List_Group_Form(request.GET)
    students = ''

    if request.method == 'GET':

        if 'group' in request.GET and request.GET['group']:
            group = get_object_or_404(Group_Contingent, id=request.GET['group'])
            students = group.students.all()
            # Student.objects.filter(id_group=group)
        else:
            group = ''

        context = {
            'student': students,
            'form': form,
            'group': group,
        }
    return render(request, 'info/list_group.html', context=context)


def list_group_create(request, id_group):
    if not request.user.is_teacher and not request.user.is_staf:
        return redirect("/")
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    students = Group_Contingent.objects.get(id=id_group).students.all()
    nomera = workbook.add_format()
    nomera.set_align('center')
    nomera.set_align('vcenter')
    nomera.set_border()
    fio = workbook.add_format()
    fio.set_align('left')
    fio.set_align('vcenter')
    fio.set_border()
    # Get some data to write to the spreadsheet.
    data = students
    name_group = Group_Contingent.objects.get(id=id_group).name
    worksheet.write(0, 0, f'Группа: {name_group}')
    worksheet.write(1, 0, f'№', nomera)
    worksheet.write(1, 1, f'Фамилия', fio)
    worksheet.write(1, 2, f'Имя', fio)
    worksheet.write(1, 3, f'Отчество', fio)
    worksheet.write(1, 4, f'Примечание', fio)
    # Write some test data.
    worksheet.set_column(1, 1, 20)
    worksheet.set_column(1, 2, 20)
    worksheet.set_column(1, 3, 20)
    worksheet.set_column(1, 4, 20)
    for row_num, columns in enumerate(data):
        worksheet.write(row_num + 2, 0, row_num + 1, nomera)
        worksheet.write(row_num + 2, 1, columns.last_name, fio)
        worksheet.write(row_num + 2, 2, columns.first_name, fio)
        worksheet.write(row_num + 2, 3, columns.second_name, fio)
        if columns.starosta == True:
            worksheet.write(row_num + 2, 4, 'Староста', fio)
        else:
            worksheet.write(row_num + 2, 4, '', fio)

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    filename = name_group + '.xlsx'

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


@login_required()
def add_subjects(request):
    form = Add_Subjects(request.GET)
    if not request.user.is_staf:
        return redirect("/")

    if request.method == 'POST':
        student = request.POST['student']
        subject = request.POST['subject']

        student = Student.objects.get(id=student)

        student.subjects.add(subject)
        student.save()

    context = {

        'form': form,

    }

    return render(request, 'info/add_subjects.html', context=context)


class GroupAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Group_Contingent.objects.none()
        groups = Teacher.objects.get(id_teacher=self.request.user.teacher.id_teacher).groups.all()

        if self.q:
            groups = groups.filter(Q(name__icontains=self.q) | Q(name__istartswith=self.q))
        return groups


class GroupAutocomplete_all(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Group_Contingent.objects.none()
        groups = Group_Contingent.objects.all()

        if self.q:
            groups = groups.filter(Q(name__icontains=self.q) | Q(name__istartswith=self.q))
        return groups


class Group_and_SubjectAutocomplete_all(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Group_and_Subject.objects.none()

        item = Group_and_Subject.objects.all()

        if self.q:
            item = item.filter(Q(subject__name__icontains=self.q) | Q(subject__name__istartswith=self.q) | Q(
                group__name__icontains=self.q) | Q(group__name__istartswith=self.q))
        return item


class Group_and_SubjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Group_and_Subject.objects.none()

        item = Teacher.objects.get(id_teacher=self.request.user.teacher.id_teacher).group_and_subjects.all()

        if self.q:
            item = item.filter(Q(subject__name__icontains=self.q) | Q(subject__name__istartswith=self.q) | Q(
                group__name__icontains=self.q) | Q(group__name__istartswith=self.q))
        return item


class SubjectAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Subject.objects.none()

        subjects = Teacher.objects.get(id_teacher=self.request.user.teacher.id_teacher).subjects.all()

        if self.q:
            subjects = subjects.filter(Q(name__icontains=self.q) | Q(name__istartswith=self.q))

        return subjects


class SubjectAutocomplete_all(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Subject.objects.none()

        subjects = Subject.objects.all()

        if self.q:
            subjects = subjects.filter(Q(name__icontains=self.q) | Q(name__istartswith=self.q))

        return subjects


class TeacherAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Teacher.objects.none()

        teachers = Teacher.objects.filter(status=True)

        if self.q:
            teachers = teachers.filter(
                Q(last_name__icontains=self.q) | Q(first_name__icontains=self.q) | Q(second_name__icontains=self.q))

        return teachers


class StudentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Student.objects.none()

        students = Student.objects.all()

        if self.q:
            students = students.filter(
                Q(last_name__icontains=self.q) | Q(first_name__icontains=self.q) | Q(second_name__icontains=self.q) | Q(
                    last_name__istartswith=self.q))

        return students


class Group_and_SubjectAutocomplete_Student(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Group_and_Subject.objects.none()

        subjects = Group_and_Subject.objects.all()

        if self.q:
            subjects = subjects.filter(Q(subject__name__icontains=self.q) | Q(subject__name__istartswith=self.q) | Q(
                group__name__icontains=self.q) | Q(group__name__istartswith=self.q))

        return subjects


class School_Subjects_dopAutocomplete_School(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = School_Subjects_dop.objects.filter(~Q(subject__name='Информатика'))

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class School_SubjectsAutocomplete_School(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = School_Subjects.objects.filter(~Q(name='Информатика'))

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class SchoolEditView(UpdateView):
    model = School
    form_class = SchoolForm
    template_name = 'info/school_edit.html'
    # fields = ['__all__']
    # fields = ['last_name', 'first_name', 'second_name', 'phone_number', 'date_of_birth', 'vk_link', 'fio_parent', 'phone_number_parent', 'school', 'class_number', 'subject', 'format']
    success_url = reverse_lazy('index')


@login_required()
def all_schools(request):
    if not request.user.is_sish:
        return redirect("/")
    form = View_Schools(request.GET)
    schools = School.objects.filter(user__is_active=True)
    # schools = School.objects.filter(user__is_active=True)
    if request.method == 'GET':

        if 'end_date' in request.GET and request.GET['end_date'] and not request.GET['start_date']:
            get_end_date = (request.GET['end_date'])
            schools = schools.filter(time_create__lte=get_end_date)
        if 'start_date' in request.GET and request.GET['start_date']:
            get_start_date = (request.GET['start_date'])
            schools = schools.filter(time_create__gte=get_start_date)
            if 'end_date' in request.GET and request.GET['end_date']:
                get_end_date = (request.GET['end_date'])
                schools = schools.filter(time_create__range=(get_start_date, get_end_date))

    context = {
        'schools': schools,
        'form': form,

    }

    return render(request, 'info/school_view.html', context=context)


def list_schools(request):
    if not request.user.is_sish and not request.user.is_staf:
        return redirect("/")
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    schools = School.objects.all()
    nomera = workbook.add_format()
    nomera.set_align('center')
    nomera.set_align('vcenter')
    nomera.set_border()
    fio = workbook.add_format()
    fio.set_align('left')
    fio.set_align('vcenter')
    fio.set_border()
    # Get some data to write to the spreadsheet.
    data = schools

    worksheet.write(1, 0, f'№', nomera)
    worksheet.write(1, 1, f'Дата регистрации', nomera)
    worksheet.write(1, 2, f'Фамилия', fio)
    worksheet.write(1, 3, f'Имя', fio)
    worksheet.write(1, 4, f'Отчество', fio)
    worksheet.write(1, 5, f'Номер телефона', fio)
    worksheet.write(1, 6, f'Дата рождения', fio)
    worksheet.write(1, 7, f'VK', fio)
    worksheet.write(1, 8, f'ФИО Родителя', fio)
    worksheet.write(1, 9, f'Номер телефона', fio)
    worksheet.write(1, 10, f'Школа', fio)
    worksheet.write(1, 11, f'Класс', fio)
    worksheet.write(1, 12, f'Предметы', fio)
    worksheet.write(1, 13, f'Формат', fio)
    worksheet.write(1, 14, f'Доп. предметы', fio)
    worksheet.write(1, 15, f'Город', fio)
    # Write some test data.
    worksheet.set_column(1, 1, 10)
    worksheet.set_column(1, 2, 30)
    worksheet.set_column(1, 3, 10)
    worksheet.set_column(1, 4, 10)
    worksheet.set_column(1, 5, 40)
    worksheet.set_column(1, 4, 20)
    worksheet.set_column(1, 12, 30)
    worksheet.set_column(1, 14, 30)
    for row_num, columns in enumerate(data):
        worksheet.write(row_num + 2, 0, row_num + 1, nomera)
        worksheet.write(row_num + 2, 1, columns.time_create.strftime("%d.%m.%Y"), fio)
        worksheet.write(row_num + 2, 2, columns.last_name, fio)
        worksheet.write(row_num + 2, 3, columns.first_name, fio)
        worksheet.write(row_num + 2, 4, columns.second_name, fio)
        worksheet.write(row_num + 2, 5, columns.phone_number, fio)
        worksheet.write(row_num + 2, 6, columns.date_of_birth.strftime("%d.%m.%Y"), fio)
        worksheet.write(row_num + 2, 7, columns.vk_link, fio)
        worksheet.write(row_num + 2, 8, columns.fio_parent, fio)
        worksheet.write(row_num + 2, 9, columns.phone_number_parent, fio)
        worksheet.write(row_num + 2, 10, columns.school, fio)

        worksheet.write(row_num + 2, 11, str(SCHOOL_CHOICES_CLASS_NUMBER[int(columns.class_number) - 1][1]), fio)
        a = ''
        for subject in columns.subject.all():
            a = a + ' ' + str(subject)
        worksheet.write(row_num + 2, 12, a, fio)
        worksheet.write(row_num + 2, 13, str(SCHOOL_CHOICES_FORMAT[int(columns.format) - 1][1]), fio)
        b = ''
        for subject in columns.subject_dop.all():
            b = b + ' ' + str(subject)
        worksheet.write(row_num + 2, 14, b, fio)
        worksheet.write(row_num + 2, 15, columns.town, fio)
    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    filename = str(datetime.datetime.today()) + '.xlsx'

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
