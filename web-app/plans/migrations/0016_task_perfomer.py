# Generated by Django 4.1.4 on 2023-03-23 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0015_remove_patterntask_dey_ofset_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='perfomer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='plans.perfomer', verbose_name='Исполнитель'),
            preserve_default=False,
        ),
    ]
