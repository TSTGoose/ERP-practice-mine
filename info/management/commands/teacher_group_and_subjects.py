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
        def get_subjects():
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
                        print(i[2])
                        #print(Teacher.objects.get(id_teacher=i[0]), Subject.objects.get(name=i[1]), Group_Contingent.objects.get(id_group_rasp=i[2], period = Period.objects.last()))
                        try:    
                            teacher = Teacher.objects.get(id_teacher=i[0])
                            subject = Subject.objects.get(name=i[1])
                            group = Group_Contingent.objects.get(id_group_rasp=i[2], period = Period.objects.last())
                            print(group,subject)
                            teacher.group_and_subjects.add (Group_and_Subject.objects.get(subject=subject, group=group))
                            teacher.save()
                        except:
                            pass
        get_subjects()