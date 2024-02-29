from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
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
                                    teacher.groups.add(Group_Contingent.objects.get(id_group_rasp=item[0], period=Period.objects.last()) )
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
            
