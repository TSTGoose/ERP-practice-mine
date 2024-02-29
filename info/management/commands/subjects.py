from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
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


        