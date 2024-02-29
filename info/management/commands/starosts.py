from venv import create
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
import pymysql, json, datetime
from datetime import date

from info.models import *

from urllib import response
import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    def handle(self, *args, **kwargs):      
        def get_groups():
            params = {
                'login' : 'api_user',
                'password' : 'PL6BLIi3hyo9VnL6Bq12hV1ez',
                'g_year' : "2022/2023",

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