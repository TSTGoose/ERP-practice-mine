# Generated by Django 4.1 on 2023-02-05 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0033_rename_id_group_group_contingent_id_group_contingent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='id_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info.group_contingent', verbose_name='Номер группы'),
        ),
    ]
