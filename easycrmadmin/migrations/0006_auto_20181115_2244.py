# Generated by Django 2.1.2 on 2018-11-15 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('easycrmadmin', '0005_auto_20181115_2147'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='basepermission',
            options={'permissions': (('view_task', 'View task'),), 'verbose_name': '动态权限存储类', 'verbose_name_plural': '动态权限存储类'},
        ),
    ]