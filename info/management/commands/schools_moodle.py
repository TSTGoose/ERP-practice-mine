from venv import create
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
import pymysql, json, datetime
from datetime import date

from info.models import *

from urllib import response
import requests
from bs4 import BeautifulSoup
import certifi
import urllib3
import time
import ssl


requests.packages.urllib3.disable_warnings()
token = '50ca701a1b5728141ce996c37a8c23db' #es
#token = '690c69b0770305f4c416fcbe710c6e1a'
url='https://es.ssti.ru/webservice/rest/server.php'
#("1", "9 класс"),("2", "10 класс"),("3", "11 класс"),

#rp = requests.get(url='http://es.ssti.ru', verify=False)
#print(rp.text)
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

     
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
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
                            #print(data)
                            time.sleep(2)
                            print(rp.text)
                            #school.status = True
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