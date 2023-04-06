# Generated by Django 4.1.4 on 2023-03-23 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_userdeteil_options'),
        ('plans', '0017_patterntask_divisin_perfomer_perfomer_division_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='user_creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='plan_creator', to='accounts.userdeteil', verbose_name='Создатель'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='plan',
            name='user_updater',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='plan_updater', to='accounts.userdeteil', verbose_name='Создатель'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='user_creator',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='task_creator', to='accounts.userdeteil', verbose_name='Создатель'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='user_updater',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='task_updater', to='accounts.userdeteil', verbose_name='Создатель'),
            preserve_default=False,
        ),
    ]
