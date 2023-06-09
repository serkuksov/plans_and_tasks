# Generated by Django 4.1.4 on 2023-03-15 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0014_alter_plan_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patterntask',
            name='dey_ofset',
        ),
        migrations.RemoveField(
            model_name='patterntask',
            name='month_ofset',
        ),
        migrations.RemoveField(
            model_name='patterntask',
            name='year_ofset',
        ),
        migrations.AddField(
            model_name='patterntask',
            name='days_ofset',
            field=models.CharField(default='0', help_text='Введите смещение: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение дней'),
        ),
        migrations.AddField(
            model_name='patterntask',
            name='months_ofset',
            field=models.CharField(default='0', help_text='Введите смещение: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение месяцев'),
        ),
        migrations.AddField(
            model_name='patterntask',
            name='years_ofset',
            field=models.CharField(default='0', help_text='Введите смещение: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение лет'),
        ),
        migrations.AlterField(
            model_name='task',
            name='pattern_task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='plans.patterntask', verbose_name='Шаблонная задача'),
        ),
    ]
