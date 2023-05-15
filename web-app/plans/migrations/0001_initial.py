# Generated by Django 4.2 on 2023-05-15 07:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0005_alter_userdeteil_options_alter_userdeteil_division_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatternPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, verbose_name='Краткое имя шаблона плана')),
                ('description', models.TextField(verbose_name='Имя шаблона плана')),
            ],
            options={
                'verbose_name': 'Шаблон Плана-графика',
                'verbose_name_plural': 'Шаблоны Планов-графиков',
            },
        ),
        migrations.CreateModel(
            name='PatternTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Имя шаблонной задачи')),
                ('days_ofset', models.CharField(default='0', help_text='Введите смещение дней: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение дней')),
                ('months_ofset', models.CharField(default='0', help_text='Введите смещение месяцев: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение месяцев')),
                ('years_ofset', models.CharField(default='0', help_text='Введите смещение лет: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра', max_length=4, verbose_name='Смещение лет')),
                ('divisin_perfomer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.division', verbose_name='Подразделение исполнителя')),
                ('pattern_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plans.patternplan', verbose_name='Шаблонный План-график')),
            ],
            options={
                'verbose_name': 'Шаблон задачи',
                'verbose_name_plural': 'Шаблоны задач',
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Краткое имя плана')),
                ('description', models.TextField(verbose_name='Имя плана')),
                ('completion_date', models.DateField(verbose_name='Планируямая дата завершения')),
                ('date_of_creation', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_of_update', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('pattern_plan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='plans.patternplan', verbose_name='Шаблонный План-график')),
                ('user_creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plan_creator', to='accounts.userdeteil', verbose_name='Создатель')),
                ('user_updater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plan_updater', to='accounts.userdeteil', verbose_name='Последний редактор')),
            ],
            options={
                'verbose_name': 'План-график',
                'verbose_name_plural': 'План-графики',
            },
        ),
        migrations.CreateModel(
            name='TaskGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Имя группы')),
            ],
            options={
                'verbose_name': 'Группа задачи',
                'verbose_name_plural': 'Группы задач',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Имя задачи')),
                ('completion_date', models.DateField(verbose_name='Дата выполнения')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активная?')),
                ('date_of_creation', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_of_update', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('pattern_task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='plans.patterntask', verbose_name='Шаблонная задача')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='plans.plan', verbose_name='План-график')),
                ('user_creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_creator', to='accounts.userdeteil', verbose_name='Создатель')),
                ('user_updater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='task_updater', to='accounts.userdeteil', verbose_name='Последний редактор')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
            },
        ),
        migrations.CreateModel(
            name='Perfomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.division', verbose_name='Подразделение исполнителя')),
                ('performer_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.userdeteil', verbose_name='Исполнитель')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='plans.task', verbose_name='Исполнитель')),
            ],
            options={
                'verbose_name': 'Исполнитель',
                'verbose_name_plural': 'Исполнители',
            },
        ),
        migrations.AddField(
            model_name='patterntask',
            name='task_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='plans.taskgroup', verbose_name='Группа задач'),
        ),
    ]
