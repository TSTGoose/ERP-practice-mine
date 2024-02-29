from django.core.management.base import BaseCommand
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test message body',
    'es.ssti@yandex.ru',
    ['avsavenko@mephi.ru'],
    fail_silently=False,
)