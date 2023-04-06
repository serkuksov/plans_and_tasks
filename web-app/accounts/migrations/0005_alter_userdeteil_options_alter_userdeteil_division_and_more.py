# Generated by Django 4.1.4 on 2023-03-30 11:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_userdeteil_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdeteil',
            options={'verbose_name': 'Дополнительные данные пользователя', 'verbose_name_plural': 'Дополнительные данные пользователей'},
        ),
        migrations.AlterField(
            model_name='userdeteil',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.division', verbose_name='Подразделение'),
        ),
        migrations.AlterField(
            model_name='userdeteil',
            name='phone_number',
            field=models.PositiveSmallIntegerField(blank=True, unique=True, validators=[django.core.validators.MinValueValidator(3200), django.core.validators.MaxValueValidator(3399)], verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='userdeteil',
            name='second_name',
            field=models.CharField(blank=True, max_length=20, verbose_name='Отчество'),
        ),
    ]
