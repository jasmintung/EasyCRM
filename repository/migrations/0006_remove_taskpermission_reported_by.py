# Generated by Django 2.1.2 on 2018-11-25 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_auto_20181125_1514'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskpermission',
            name='reported_by',
        ),
    ]