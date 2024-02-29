from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *

type = {
    'Лабораторная':1,
    'Практика':0,
    'Лекция':2,
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        
       for item in type:
            print(item)
            type_lesson = Type_lesson()
            type_lesson.id_type = type[item]
            type_lesson.name = item
            type_lesson.save()

                                
                        
            
