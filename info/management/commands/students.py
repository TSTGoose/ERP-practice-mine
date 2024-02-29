from venv import create
from django.core.management.base import BaseCommand
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
import pymysql, json, datetime
from datetime import date

from info.models import *

from urllib import response
import requests
from bs4 import BeautifulSoup


def expelled_student():
    students = Student.objects.all()
    for stud in students:
        params = {
            'login': 'api_user',
            'password': 'PL6BLIi3hyo9VnL6Bq12hV1ez',
            'id': stud.id_people,
        }
        rpp = requests.get('http://83.172.33.133/students_api/by_person_id.json', params=params, verify=False)
        if rpp.json() == []:
            stud.expelled = True
            stud.save()
        else:
            stud.expelled = False
            stud.save()


def get_student():
    students = []

    params = {
        'login': 'api_user',
        'password': 'PL6BLIi3hyo9VnL6Bq12hV1ez',
    }

    rpp = requests.get('http://83.172.33.133/students_api/index.json', params=params, verify=False)
    # rp = requests.get('http://83.172.33.133/students_api/groups_list.json', params=params, data=data, verify=False)
    # print(rp)
    for i in rpp.json():
        # print(i)
        students.append({
            'id_people': i['id'],
            'last_name': i['last_name'],
            'first_name': i['first_name'],
            'second_name': i['second_name'],
            'group': i['group']
        })
        # print(students)
    return students


def transliterate(name):
    # Слоаврь с заменами
    slovar = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'i',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'tc',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ъ': '',
        'ы': 'u',
        'ь': '',
        'э': 'e',
        'ю': 'iu',
        'я': 'ia',
        'А': 'A',
        'Б': 'B',
        'В': 'V',
        'Г': 'G',
        'Д': 'D',
        'Е': 'E',
        'Ё': 'E',
        'Ж': 'ZH',
        'З': 'Z',
        'И': 'I',
        'Й': 'I',
        'К': 'K',
        'Л': 'L',
        'М': 'M',
        'Н': 'N',
        'О': 'O',
        'П': 'P',
        'Р': 'R',
        'С': 'S',
        'Т': 'T',
        'У': 'U',
        'Ф': 'F',
        'Х': 'KH',
        'Ц': 'TC',
        'Ч': 'CH',
        'Ш': 'SH',
        'Щ': 'SHCH',
        'Ъ': '',
        'Ы': 'U',
        'Ь': '',
        'Э': 'E',
        'Ю': 'IU',
        'Я': 'IA',
        '-': '',
        '_': '',
        'A': 'a',
        'B': 'b',
        'C': 'c',
        'D': 'd',
        'E': 'e',
        'F': 'f',
        'G': 'g',
        'H': 'h',
        'I': 'i',
        'J': 'j',
        'K': 'k',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'O': 'o',
        'P': 'p',
        'Q': 'q',
        'R': 'r',
        'S': 's',
        'T': 't',
        'U': 'u',
        'V': 'v',
        'W': 'w',
        'Z': 'z',
        'X': 'x',
        'Y': 'y', }

    # Циклически заменяем все буквы в строке
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        result = []
        expelled_student()
        for i in get_student():
            print(i['id_people'], i)
            if len(i['group']) > 1 and Group.objects.filter(name=i['group']).exists():
                # print(get_object_or_404(Group, name=i['group'], status=True))
                try:
                    print(i['id_people'])
                    student = Student.objects.get(id_people=i['id_people'])
                    student.id_people = i['id_people']
                    student.id_group = Group.objects.get(name=i['group'], status=True)
                    student.last_name = i['last_name']
                    student.first_name = i['first_name']
                    student.second_name = i['second_name']
                    student.save()
                    print(student, Group.objects.get(name=i['group'], status=True), 'obnovil')
                    result.append({
                        'fio': (i['last_name']) + ' ' + (i['first_name']) + ' ' + (i['second_name']),
                        'group': i['group'],
                        'login': student.user.username,
                        'password': transliterate(i['group'].lower()) + transliterate(
                            i['first_name'][0].lower()) + transliterate(i['second_name'][0].lower()) + transliterate(
                            i['last_name'].lower()) + "@",
                    })
                except:
                    try:
                        user = User.objects.create_user(
                            username=transliterate(i['group'].lower()) + transliterate(
                                i['first_name'][0].lower()) + transliterate(
                                i['second_name'][0].lower()) + transliterate(i['last_name'].lower()),
                            password=transliterate(i['group'].lower()) + transliterate(
                                i['first_name'][0].lower()) + transliterate(
                                i['second_name'][0].lower()) + transliterate(i['last_name'].lower()) + "@",
                        )
                        user.save()
                        print(user, 'sozdan')
                        Student.objects.update_or_create(
                            user=user,
                            id_people=i['id_people'],
                            id_group=Group.objects.get(name=i['group'], status=True),
                            last_name=i['last_name'],
                            first_name=i['first_name'],
                            second_name=i['second_name'],
                        )
                        result.append({
                            'fio': (i['last_name']) + ' ' + (i['first_name']) + ' ' + (i['second_name']),
                            'group': i['group'],
                            'login': transliterate(i['group'].lower()) + transliterate(
                                i['first_name'][0].lower()) + transliterate(
                                i['second_name'][0].lower()) + transliterate(i['last_name'].lower()),
                            'password': transliterate(i['group'].lower()) + transliterate(
                                i['first_name'][0].lower()) + transliterate(
                                i['second_name'][0].lower()) + transliterate(i['last_name'].lower()) + "@",
                        })
                    except:
                        try:
                            user = User.objects.get(username=transliterate(i['group'].lower()) + transliterate(
                                i['first_name'][0].lower()) + transliterate(
                                i['second_name'][0].lower()) + transliterate(i['last_name'].lower()))
                            print(user, 'est')
                            print(i['last_name'], i['id_people'], Group.objects.get(name=i['group'], status=True))
                            Student.objects.update_or_create(
                                user=user,
                                id_people=i['id_people'],
                                id_group=Group.objects.get(name=i['group'], status=True),
                                last_name=i['last_name'],
                                first_name=i['first_name'],
                                second_name=i['second_name'],
                            )
                            print('obnovil')
                        except:
                            try:
                                student = Student.objects.get(id_people=i['id_people'])
                                print(student, Group.objects.get(name=i['group']))
                                student.id_people = i['id_people']
                                student.id_group = Group.objects.get(name=i['group'], status=True)
                                student.last_name = i['last_name']
                                student.first_name = i['first_name']
                                student.second_name = i['second_name']
                                student.save()
                                print(student, Group.objects.get(name=i['group'], status=True), 'obnovil')
                            except:
                                pass

        print(result)
        with open(('students.json'), 'w', encoding='utf-8') as file:
            json.dump(result, file, indent=4, ensure_ascii=False)
