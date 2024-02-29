from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
       groups = Group.objects.all()
       for group in groups:
            if Period.objects.last().date_start.year - int(group.year_priem) < 6:
                group.status=True
                group.save()
            else:
                group.status=False
                group.save()
    