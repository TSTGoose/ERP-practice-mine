from django.core.management.base import BaseCommand

import pymysql
import json

from info.models import *


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
    'Y': 'y',}
        
   # Циклически заменяем все буквы в строке
        for key in slovar:
            name = name.replace(key, slovar[key])
        return name


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
            result = []
            with pymysql.connect(host="83.172.33.149", user='phpscript1', password='pFDqwG4c', database="sti",) as connection:
                with connection.cursor() as cursor:
                    query = 'SELECT id, surname, name, patronymic, work FROM `teachers`'
                    cursor.execute(query)
                    for item in cursor:
                        #print(item)
                        #print(transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()) + "@")
                        result.append({
                            'fio':item[1] + ' ' + item[2] + ' ' + item[3],
                            'login':transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()),
                            'password':(transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()) + "@"),
                        })
                        if Teacher.objects.filter(id_teacher=item[0]).exists():
                            print(item[1])
                            teacher = Teacher.objects.get(id_teacher=item[0])
                            
                            teacher.last_name=item[1]
                            teacher.first_name =item[2]
                            teacher.second_name=item[3]
                            teacher.status=item[4]
                            teacher.save()
                            print(teacher,'obnovil')
                        else:  
                            if User.objects.filter(username=transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower())).exists():
                                user = User.objects.get(username=transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()))
                                print(user, 'est')
                                if not Teacher.objects.filter(id_teacher=item[0]).exists():
                                    try:
                                        Teacher.objects.create(
                                    user=user,
                                    id_teacher = item[0],
                                    last_name = item[1],
                                    first_name = item[2],
                                    second_name = item[3],
                                    status = item[4],
                                    post = Post.objects.get(id=1),
                                    )
                                    except:
                                        pass
                            else:
                                user = User.objects.create_user(
                                username=transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()),
                                password=transliterate(transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()) + "@"),
                                    )
                                user.save()
                                print(user, 'sozdan')
                                Teacher.objects.create(
                                    user=user,
                                    id_teacher = item[0],
                                    last_name = item[1],
                                    first_name = item[2],
                                    second_name = item[3],
                                    status = item[4],
                                    post = Post.objects.get(id=1),
                                    )
                                result.append({
                                        'fio':item[1] + ' ' + item[2] + ' ' + item[3],
                                        'login':transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()),
                                        'password':(transliterate(item[2][0].lower()) + transliterate(item[3][0].lower()) + transliterate(item[1].lower()) + "@"),
                                    })




                            
                            
            with open(('teachers.json'), 'w', encoding='utf-8') as file:
                json.dump(result, file, indent=4, ensure_ascii=False)
        