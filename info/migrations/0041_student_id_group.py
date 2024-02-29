# Generated by Django 4.1 on 2023-02-05 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0040_remove_student_id_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='id_group',
            field=models.ForeignKey(blank=True, default=0, on_delete=django.db.models.deletion.CASCADE, to='info.group_contingent', verbose_name='Номер группы'),
            preserve_default=False,
        ),
    ]
