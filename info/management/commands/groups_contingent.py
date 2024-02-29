from venv import create
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
import pymysql, json, datetime
from datetime import date
from transliterate import translit, get_available_language_codes
from info.models import *
import random
from urllib import response
import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    def handle(self, *args, **kwargs):      

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
                    #print(stud['id'],Student.objects.get(id_people=stud['id']).id_people)
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
                        if stud['id'] != Student.objects.get(id_people=stud['id']).id_people:
                            print(Student.objects.get(id_people=stud['id']))
                        
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
            with open(('students.json'), 'a', encoding='utf-8') as file:
                json.dump(result, file, indent=4, ensure_ascii=False)


        get_groups()