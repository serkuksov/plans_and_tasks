# Generated by Django 4.1.4 on 2023-03-14 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0013_alter_patternplan_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='description',
            field=models.TextField(verbose_name='Имя плана'),
        ),
    ]
