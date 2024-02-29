from venv import create
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
import pymysql, json, datetime
from datetime import date
from transliterate import translit, get_available_language_codes
from info.models import *

from urllib import response
import requests
from bs4 import BeautifulSoup
import certifi
import urllib3
import time
from celery import shared_task
from django_celery_beat.models import PeriodicTask


@shared_task(name="schooles_moodle")
def schooles_moodle():    
    requests.packages.urllib3.disable_warnings()
    http = urllib3.PoolManager()
    token = '50ca701a1b5728141ce996c37a8c23db' #es
    #token = '690c69b0770305f4c416fcbe710c6e1a'
    url='https://es.ssti.ru/webservice/rest/server.php/'
    #("1", "9 класс"),("2", "10 класс"),("3", "11 класс"),
    headers = urllib3.util.make_headers(user_agent= 'my-agent/1.0.1', basic_auth='abc:xyz')

    id_groups_moodle_subjects = {
        '1':{
            '1':{
                'Математика':27,
                'Физика':28,
                'Химия':29
            },
            '2':{
                'Математика':26,
                'Физика':25,
                'Химия':24
            },
            '3':{
                'Математика':12,
                'Физика':13,
                'Химия':14
            }
            }
    }
    id_groups_moodle_class = {
        '1':{
            '1':21,
            '2':20,
            '3':11
            }
    }

    schools = School.objects.all()
    moodledata = {}
    #moodledata.update('users')
    for school in schools:
        if school.user.is_active:   
            if school.status == False:
                #print(school.format)
                if school.format == '1':
                    #print(school)
                    params = {
                                    'wstoken': token,
                                    'wsfunction': 'core_user_create_users',
                                    'moodlewsrestformat':'json',
                                    "users[0][username]":school.user.username,
                                    "users[0][createpassword]":'1',
                                    "users[0][firstname]":str(school.first_name) + ' ' + str(school.second_name),
                                    "users[0][lastname]":school.last_name,
                                    "users[0][email]":school.user.email,
                                    }
                    rp = requests.post(url, params=params, verify=False)
                            
                    time.sleep(2)
                    print(rp.text)
                            
                    school.save()
                    params = {
                                    'wstoken': token,
                                    'wsfunction': 'core_cohort_add_cohort_members',
                                    'moodlewsrestformat':'json',
                                    "members[1][cohorttype][type]":'id',
                                    "members[1][cohorttype][value]":id_groups_moodle_class['1'][school.class_number],
                                    "members[1][usertype][type]":"username",
                                    "members[1][usertype][value]":school.user.username,
                                    
                                    }
                    rp = requests.post(url, params=params, verify=False)
                    time.sleep(2)
                            #print(data)
                            #print(rp.json())
                    for sub in school.subject.all():
                        if sub.name == 'Информатика':
                            continue
                                #print(sub.name)
                        params = {
                                    'wstoken': token,
                                    'wsfunction': 'core_cohort_add_cohort_members',
                                    'moodlewsrestformat':'json',
                                    "members[1][cohorttype][type]":'id',
                                    "members[1][cohorttype][value]":id_groups_moodle_subjects['1'][school.class_number][sub.name],
                                    "members[1][usertype][type]":"username",
                                    "members[1][usertype][value]":school.user.username,
                                    
                                    }
                        rp = requests.post(url, params=params, verify=False)
                        time.sleep(2)
                                #print(data)
                                #print(rp.json()) 
                    for sub in school.subject_dop.all():
                        if sub.subject.name == 'Информатика':
                            continue
                        if sub.format == '1':   
                            params = {
                                        'wstoken': token,
                                        'wsfunction': 'core_cohort_add_cohort_members',
                                        'moodlewsrestformat':'json',
                                        "members[1][cohorttype][type]":'id',
                                        "members[1][cohorttype][value]":id_groups_moodle_subjects['1'][sub.class_number][sub.subject.name],
                                        "members[1][usertype][type]":"username",
                                        "members[1][usertype][value]":school.user.username,
                                        
                                        }
                            rp = requests.post(url, params=params, verify=False)
                            time.sleep(2)
                                    #print(data)
                                    #print(rp.json())    
                else:
                    for sub in school.subject_dop.all():
                        if sub.subject.name == 'Информатика':
                            continue
                        if sub.format == '1':
                            params = {
                                    'wstoken': token,
                                    'wsfunction': 'core_user_create_users',
                                    'moodlewsrestformat':'json',
                                    "users[0][username]":school.user.username,
                                    "users[0][createpassword]":'1',
                                    "users[0][firstname]":str(school.first_name) + ' ' + str(school.second_name),
                                    "users[0][lastname]":school.last_name,
                                    "users[0][email]":school.user.email,
                                    }
                            rp = requests.post(url, params=params, verify=False)
                                    #print(data)
                            time.sleep(2)
                            print(rp.text)   
                            params = {
                                        'wstoken': token,
                                        'wsfunction': 'core_cohort_add_cohort_members',
                                        'moodlewsrestformat':'json',
                                        "members[1][cohorttype][type]":'id',
                                        "members[1][cohorttype][value]":id_groups_moodle_subjects['1'][sub.class_number][sub.subject.name],
                                        "members[1][usertype][type]":"username",
                                        "members[1][usertype][value]":school.user.username,
                                        
                                        }
                            rp = requests.post(url, params=params, verify=False)
                            time.sleep(2)    


@shared_task(name="groups")
def groups():
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT id, name, year_priem, enabled, semestr FROM `group`'
            cursor.execute(query)
            for item in cursor:
                #print(item)
                
                try:
                    try:
                        print(item[1], 'sozdan')
                        group = Group()
                        group.id_group = item[0]
                        group.name = item[1]
                        group.year_priem = item[2]
                        group.status = item[3]
                        group.semestr = item[4]
                        group.save()
                    except:
                        print(item[1], 'update')
                        group = Group.objects.get(name=item[1])
                        group.id_group = item[0]
                        group.year_priem = item[2]
                        group.status = item[3]
                        group.semestr = item[4]
                        group.save()
                        #pass
                        
                except:
                    pass


@shared_task(name="groups_contingent")
def groups_contingent():
    def get_id_group(name):
            with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
                with connection.cursor() as cursor:
                   
                    query =  f"""SELECT id, name, enabled
                        FROM `group`
                        WHERE name = '{name}'
                        AND enabled = 1"""              
                    cursor.execute(query)
                    
                    for item in cursor:
                        pass
            return item[0]
    def get_groups():
        result = []
        params = {
        'login' : 'api_user',
        'password' : 'PL6BLIi3hyo9VnL6Bq12hV1ez',
        }
        rp = requests.get('http://83.172.33.133/students_api/groups_list.json', params=params, verify=False)

        for group in rp.json():
            if '/' in group['name']:
                continue
            rpp = requests.get(f'http://83.172.33.133/students_api/group_info.json?login=api_user&password=PL6BLIi3hyo9VnL6Bq12hV1ez&id={group["id"]}', verify=False)
            term = ''
            if rpp.json()['group']['term'] == 'осень':
                term = 1
            else:
                term = 2
            print(term)
            get_group = requests.get(f"http://83.172.33.133/students_api/by_term.json?year={rpp.json()['group']['study_year']}&term={term}&group_name={group['name']}&login=api_user&password=PL6BLIi3hyo9VnL6Bq12hV1ez", verify=False)
            per = rpp.json()['group']['term'] + ' ' + rpp.json()['group']['study_year']
        #print(per)
            group_new = Group_Contingent.objects.get_or_create(id_group_contingent=group['id'], id_group_rasp=get_id_group(group['name']), name=group['name'], period=Period.objects.get(name=per)) 
            #print('est', group['id'])
            group_new[0].students.clear()
            for stud in get_group.json():
                username = (translit(stud['group'].lower(), 'ru', reversed=True) + translit(stud['first_name'][0].lower(), 'ru', reversed=True) + translit(stud['second_name'][0].lower(), 'ru', reversed=True) + translit(stud['last_name'].lower(), 'ru', reversed=True)).replace('-', '').replace("'", '')
                password = username + '@'
        #password = ''
        #for i in range(9):
            #password += random.choice('@#$1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')
            #print(stud['id'])
        
                group_new[0].study_form = rpp.json()['group']['study_form']
                group_new[0].faculty = rpp.json()['group']['faculty']
                group_new[0].level = rpp.json()['group']['level']
                group_new[0].department = rpp.json()['group']['department']['name']
                group_new[0].full_string = rpp.json()['group']['plans'][0]['full_string']
        
                group_new[0].save()
                if Student.objects.filter(id_people=stud['id']).exists():
                    group_new[0].students.add(Student.objects.get(id_people=stud['id']))
                    group_new[0].save()
                    print('Группа есть, студент есть, добавлен', stud['last_name'], group_new[0])
                    student_up = Student.objects.get(id_people=stud['id'])
                    if student_up.id_group != group_new[0]:
                        
                        student_up.id_group = group_new[0]
                        student_up.save()
                        print('Изменил группу', stud['last_name'], group_new[0])
            
                else:
                    if User.objects.filter(username=username).exists():
                        user = User.objects.get(username=username)
                        print(username)
                        Student.objects.update_or_create(
                        user=user,
                        id_people=stud['id'],
                        id_group=group_new[0],
                        last_name=stud['last_name'],
                        first_name =stud['first_name'],
                        second_name=stud['second_name'],
                        
                        )
                        group_new[0].students.add(Student.objects.get(id_people=stud['id']))
                        print('Группа есть, юзер есть, студент создан, добавлен')
                    else:
                        user = User.objects.create(
                        username=username,
                        )
                        user.set_password(password)
                        user.save()
                        Student.objects.update_or_create(
                        user=user,
                        id_people=stud['id'],
                        id_group=group_new[0],
                        last_name=stud['last_name'],
                        first_name =stud['first_name'],
                        second_name=stud['second_name'],
                        )
                        group_new[0].students.add(Student.objects.get(id_people=stud['id']))
                        print(stud['last_name'],'Группа есть, юзер создан, студент создан, добавлен')
                        result.append({
                            'fio':(stud['last_name']) + ' ' + (stud['first_name']) + ' ' + (stud['second_name']),
                            'group':stud['group'],
                            'login':Student.objects.get(id_people=stud['id']).user.username,
                            'password':password,
                        })
                group_new[0].save()
        #with open(('students.json'), 'a', encoding='utf-8') as file:
        #json.dump(result, file, indent=4, ensure_ascii=False)


    get_groups()

@shared_task(name="subjects")
def subjects():
    get_period_start = Period.objects.last().date_start.year
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            query = f"""SELECT DISTINCT subject
                        FROM `lessons`, `lessons_teachers` 
                        WHERE lessons_teachers.id_lessons = lessons.id
                        AND lessons.study_year = {get_period_start}"""
            cursor.execute(query)
            for item in cursor:
                try:
                    print(item[0])
                    Subject(name=item[0]).save()
                except:
                    pass

@shared_task(name="group_and_subject")
def group_and_subject():                        
    def main():
        groups = Group.objects.filter(status=True)
        get_period_start = Period.objects.last().date_start
        get_period_end = Period.objects.last().date_end
        date = get_period_start
        while date < get_period_end:
            print(date)    
            for group in groups:
                rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={group.id_group}&date={date}', verify=False)
                for k in rp.json()['data']:
                    try:
                        if "href" in k['subject']:
                            subject = k['subject'].split('>')[1].split('<')[0]
                        else:
                            subject = k['subject']
                        new = Group_and_Subject()
                        new.group = Group_Contingent.objects.get(id_group_rasp=group.id_group, period=Period.objects.last())
                        new.subject = Subject.objects.get(name=subject)
                        new.save()
                        print('создан', new)
                        
                    except:
                        pass
            date = (date + datetime.timedelta(days=7))
    main()
    
@shared_task(name="starosts")
def starosts():      
    def get_groups():
        params = {
            'login' : 'api_user',
            'password' : 'PL6BLIi3hyo9VnL6Bq12hV1ez',
            'g_year' : "2023/2024",

        }
        

        #rp = requests.get('http://83.172.33.133/students_api/by_term.json', params=params, data=data, verify=False)
        rp = requests.get('http://83.172.33.133/students_api/groups_list.json', params=params, verify=False)
        #print(rp)
        #for i in rp.json():
            #print(i['student_id'], i['last_name'], i['first_name'], i['second_name'])
            #print(i['name'])
        return rp.json()

    def get_students(groups):
        period=Period.objects.last()
        for group in groups:
            params = {

                'login' : 'api_user',
                'password' : 'PL6BLIi3hyo9VnL6Bq12hV1ez',
                'year' : period.name.split(' ')[1],
                'term' : period.term,
                'group_name' : group['name'],

            }
            rp = requests.get('http://83.172.33.133/students_api/by_term.json', params=params, verify=False)
            for student in rp.json():
                
                if student['elder'] == 1:
                    
                    starosta = Student.objects.get(id_people=student['id'])
                    print(starosta)
                    starosta.starosta = True
                    starosta.save()
    get_students(get_groups())


@shared_task(name="teachers")
def teachers(): 
    result = []
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            query = 'SELECT id, surname, name, patronymic, work FROM `teachers`'
            cursor.execute(query)
            for item in cursor:
                #print(item)
                #print(transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()) + "@")
                result.append({
                    'fio':item[1] + ' ' + item[2] + ' ' + item[3],
                    'login':translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()),
                    'password':(translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()) + "@"),
                })
                try:
                    print(item[1])
                    teacher = Teacher.objects.get(id_teacher=item[0])
                    
                    teacher.last_name=item[1]
                    teacher.first_name =item[2]
                    teacher.second_name=item[3]
                    teacher.status=item[4]
                    teacher.save()
                    print(teacher,'obnovil')
                except:  
                    try:
                        user = User.objects.get(username=translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()))
                        print(user, 'est')
                        Teacher.objects.update_or_create(
                        user=user,
                        
                        last_name = item[1],
                        first_name = item[2],
                        second_name = item[3],
                        status = item[4]
                        )
                        print('obnovil')    
                    except:
                        user = User.objects.create_user(
                        username=translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()),
                        password=translit(translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()) + "@"),
                            )
                        user.save()
                        print(user, 'sozdan')
                        Teacher.objects.update_or_create(
                            user=user,
                            
                            last_name = item[1],
                            first_name = item[2],
                            second_name = item[3],
                            status = item[4],
                            )
                        result.append({
                                'fio':item[1] + ' ' + item[2] + ' ' + item[3],
                                'login':translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()),
                                'password':(translit(item[2][0].lower()) + translit(item[3][0].lower()) + translit(item[1].lower()) + "@"),
                            })
        
    with open(('teachers.json'), 'w', encoding='utf-8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


@shared_task(name="teachers_subjects")
def teachers_subjects(): 
    get_period_start = Period.objects.last().date_start.year
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            teachers = Teacher.objects.all()
            for i in teachers:                      

                query = f"""SELECT DISTINCT subject 
                        FROM `lessons`, `lessons_teachers` 
                        WHERE lessons_teachers.id_lessons = lessons.id
                        AND lessons_teachers.id_teachers = {i.id_teacher}
                        AND lessons.study_year = {get_period_start}
                        AND lessons.delete = 0"""
                cursor.execute(query)
                for item in cursor:
                    #print(item, i.id_teacher)
                
                    try:
                        try:
                            print(item[0], 'sozdan')
                            teacher = i
                            print(teacher.subjects.all())
                            teacher.subjects.add(Subject.objects.get(name=item[0]) )
                            teacher.save()
                        except:
                            print(item[0], 'update')
                            '''group = Group.objects.get(name=item[1])
                            group.id_group = item[0]
                            group.year_priem = item[2]
                            group.status = item[3]
                            group.semestr = item[4]
                            group.save()'''
                            pass
                            
                    except:
                        pass


@shared_task(name="teachers_groups")
def teachers_groups(): 
    get_period_start = Period.objects.last().date_start.year
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            teachers = Teacher.objects.all()
            for i in teachers:

                query = f"""SELECT DISTINCT id_group 
                        FROM `lessons`, `lessons_teachers` 
                        WHERE lessons_teachers.id_lessons = lessons.id
                        AND lessons_teachers.id_teachers = {i.id_teacher}
                        AND lessons.study_year = {get_period_start}
                        AND lessons.delete = 0"""
                cursor.execute(query)
                for item in cursor:
                    #print(item, i.id_teacher)
                
                    try:
                        try:
                            #print(item[0], 'sozdan')
                            teacher = i
                            print(teacher, item[0])
                            teacher.groups.add(Group_Contingent.objects.get(id_group_rasp=item[0]) )
                            teacher.save()
                        except:
                            #print(item[0], 'update')
                            '''group = Group.objects.get(name=item[1])
                            group.id_group = item[0]
                            group.year_priem = item[2]
                            group.status = item[3]
                            group.semestr = item[4]
                            group.save()'''
                            pass
                            
                    except:
                        pass 


@shared_task(name="teacher_group_and_subjects")
def teacher_group_and_subjects():
    get_period_start = Period.objects.last().date_start.year
    with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
        with connection.cursor() as cursor:
            query =  f"""SELECT DISTINCT lessons_teachers.id_teachers, subject, id_group
                FROM `lessons`, `lessons_teachers` 
                WHERE lessons_teachers.id_lessons = lessons.id
                AND lessons.study_year = {get_period_start}
                AND lessons.delete = 0"""              
            cursor.execute(query)
            for i in cursor:
                try:    
                    teacher = Teacher.objects.get(id_teacher=i[0])
                    subject = Subject.objects.get(name=i[1])
                    group = Group_Contingent.objects.get(id_group_rasp=i[2])
                    print(group,subject)
                    teacher.group_and_subjects.add (Group_and_Subject.objects.get(subject=subject, group=group))
                    teacher.save()
                except:
                    pass
