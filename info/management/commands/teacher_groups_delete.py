from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        teachers = Teacher.objects.all()    
        for i in teachers:

            teacher = i
            teacher.groups.clear()
            teacher.subjects.clear()
            teacher.group_and_subjects.clear()
            teacher.save()
    
            
