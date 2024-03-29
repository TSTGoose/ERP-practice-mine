# Generated by Django 4.1 on 2023-02-05 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0032_alter_att_status_options_group_contingent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group_contingent',
            old_name='id_group',
            new_name='id_group_contingent',
        ),
        migrations.AlterUniqueTogether(
            name='group_contingent',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='group_contingent',
            name='id_group_rasp',
            field=models.CharField(default=1, max_length=100, unique=True, verbose_name='Номер группы расписание'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='group_contingent',
            unique_together={('id_group_contingent', 'id_group_rasp', 'name')},
        ),
    ]
