# Generated by Django 2.1.2 on 2018-11-12 14:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0003_auto_20181112_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studyrecord',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.Enrollment', verbose_name='学员'),
        ),
    ]
