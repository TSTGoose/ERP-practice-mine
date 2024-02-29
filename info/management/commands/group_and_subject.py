from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect
import pymysql

from info.models import *

from urllib import response
import requests
from bs4 import BeautifulSoup
import json
import datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        def main():
            groups = Group.objects.filter(status=True)
            get_period_start = Period.objects.last().date_start
            get_period_end = Period.objects.last().date_end
            date = get_period_start
            while date < get_period_end:
                print(date)    
                for group in groups:
                    rp = requests.get(f'http://raspisanie.ssti.ru/data.php?group_week={group.id_group}&date={date}', verify=False)
                    for k in rp.json()['data']:
                        try:
                            if "href" in k['subject']:
                                subject = k['subject'].split('>')[1].split('<')[0]
                            else:
                                subject = k['subject']
                            new = Group_and_Subject()
                            new.group = Group_Contingent.objects.get(id_group_rasp=group.id_group, period=Period.objects.last())
                            new.subject = Subject.objects.get(name=subject)
                            new.save()
                            print('создан', subject, group)
                            
                        except:
                            pass
                date = (date + datetime.timedelta(days=7))
        main()