from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
            with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
                with connection.cursor() as cursor:
                    query = 'SELECT id, name, year_priem, enabled, semestr FROM `group`'
                    cursor.execute(query)
                    for item in cursor:
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
                        except:
                            pass
            
