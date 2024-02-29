from django.shortcuts import render
from .forms import *
import requests
import datetime
from registration.views import *


# Формирование недели
def form_weekdays(start_week: str, format: str) -> tuple:
    print("Формирование недели")
    days_week = []
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
    print("Завершено")
    print(dict(DAYS_OF_WEEK))
    return DAYS_OF_WEEK


# Парсер расписания
def pars_timetable(request, date=datetime.datetime.today().strftime('%Y-%m-%d'), next=None, id_teacher=None,
                   id_group=None):
    print(f"Запуск парсера.\nПараметры: \nnext={next},\nid_teacher={id_teacher},\nid_group={id_group}")
    lesson = []
    groups = []
    groups_name = []
    class_matrix = [[i for i in range(7)] for j in range(7)]
    format = '%Y-%m-%d'

    if next is not None:
        print("Переменная next есть")
        date = datetime.datetime.strptime(date, format)
        date = (date + datetime.timedelta(days=int(next))).strftime(format)
        print("Изменение даты = " + date)

    if id_teacher:
        rp = requests.get(
            f'http://raspisanie.ssti.ru/data.php?teacher_week={request.user.teacher.id_teacher}&date={date}',
            verify=False)
    elif id_group:
        rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={id_group}&date={date}', verify=False)

    start_week = rp.json()['start']
    DAYS_OF_WEEK: tuple = form_weekdays(start_week=start_week, format=format)

    for i, d in enumerate(time_slots):
        for j in range(7):
            if j == 0:
                class_matrix[i][0] = d[0]
                continue
            for k in rp.json()['data']:
                if int(k['weekday']) == j and int(k['para']) - 1 == i:
                    for h in k['groups']:
                        if "href" in k['subject']:
                            subject = k['subject'].split('>')[1].split('<')[0]
                        else:
                            subject = k['subject']
                        groups.append(h['id'])
                        groups_name.append(h['name'])
                    list = dict(pairs=zip(k['id'].split(','), groups, groups_name))
                    date = ("-").join(k['date'].split('.')[::-1])
                    format = '%Y-%m-%d'
                    date_lesson = datetime.datetime.strptime(date, format)
                    lesson.append({
                        'subject': subject,
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

    if id_group is not None:
        return render(request, 'info/s_timetable.html', context)
    elif id_teacher is not None:
        return render(request, 'info/t_timetable.html', context)
    else:
        return redirect("/")
