import datetime

from django.db import models
from django.db.models import Q, Subquery
from django.urls import reverse

from accounts.models import Division, UserDeteil


class Perfomer(models.Model):
    """Модель исполнителей задач"""
    division = models.ForeignKey(Division,
                                 on_delete=models.PROTECT,
                                 verbose_name='Подразделение исполнителя',
                                 )
    performer_user = models.ForeignKey(UserDeteil,
                                       on_delete=models.PROTECT,
                                       verbose_name='Исполнитель',
                                       null=True,
                                       blank=True,
                                       )

    def __str__(self):
        if self.performer_user:
            return f'{self.division}/ {self.performer_user}'
        return f'{self.division}'
    
    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'


class PatternPlan(models.Model):
    """Модель с шаблонными планами на основе которых будут формироваться рабочие планы"""
    name = models.CharField(verbose_name='Краткое имя шаблона плана', max_length=60)
    description = models.TextField(verbose_name='Имя шаблона плана')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Шаблон Плана-графика'
        verbose_name_plural = 'Шаблоны Планов-графиков'


class Plan(models.Model):
    """Модель с рабочими планами"""
    pattern_plan = models.ForeignKey(PatternPlan,
                                     on_delete=models.SET_NULL,
                                     verbose_name='Шаблонный План-график',
                                     null=True,
                                     )
    name = models.CharField(verbose_name='Краткое имя плана', max_length=100)
    description = models.TextField(verbose_name='Имя плана')
    completion_date = models.DateField(verbose_name='Планируямая дата завершения')
    date_of_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_update = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    user_creator = models.ForeignKey(UserDeteil,
                                     on_delete=models.PROTECT,
                                     verbose_name='Создатель',
                                     related_name='plan_creator',
                                     )
    user_updater = models.ForeignKey(UserDeteil,
                                     on_delete=models.PROTECT,
                                     verbose_name='Последний редактор',
                                     related_name='plan_updater',
                                     )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plans:plan_detail', kwargs={'pk': self.pk})

    def delete(self, *args, **kwargs):
        #TODO Нужно будет переделать метод удаления исполнителей
        super().delete(*args, **kwargs)
        Perfomer.objects.filter(~Q(id__in=Subquery(Task.objects.values('perfomer_id')))).all().delete()

    def is_new_plan(self):
        """Функция проверяет новый ли план"""
        return self.date_of_creation.strftime('%Y-%m-%d %H:%M:%S') == self.date_of_update.strftime('%Y-%m-%d %H:%M:%S')

    def is_new_completion_date(self, completion_date: datetime.datetime):
        """Функция проверяет изменена ли дата выполнения плана"""
        return completion_date != self.completion_date

    class Meta:
        verbose_name = 'План-график'
        verbose_name_plural = 'План-графики'


class TaskGroup(models.Model):
    """Модель с группами задач (необхоима для корректного формирования word документов)"""
    name = models.TextField(verbose_name='Имя группы')

    def __str__(self):
        if len(self.name) > 150:
            return self.name[:150] + '...'
        return self.name

    class Meta:
        verbose_name = 'Группа задачи'
        verbose_name_plural = 'Группы задач'


class PatternTask(models.Model):
    """Шаблон задачи на основе которых формеруются рабочие задачи"""
    pattern_plan = models.ForeignKey(PatternPlan,
                                     on_delete=models.CASCADE,
                                     verbose_name='Шаблонный План-график',
                                     )
    task_group = models.ForeignKey(TaskGroup,
                                   on_delete=models.PROTECT,
                                   verbose_name='Группа задач',
                                   )
    name = models.TextField(verbose_name='Имя шаблонной задачи')
    divisin_perfomer = models.ForeignKey(Division,
                                         on_delete=models.PROTECT,
                                         verbose_name='Подразделение исполнителя',
                                         )
    days_ofset = models.CharField(
        max_length=4,
        verbose_name='Смещение дней',
        help_text='Введите смещение дней: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра',
        default='0',
    )
    months_ofset = models.CharField(
        max_length=4,
        verbose_name='Смещение месяцев',
        help_text='Введите смещение месяцев: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра',
        default='0',
    )
    years_ofset = models.CharField(
        max_length=4,
        verbose_name='Смещение лет',
        help_text='Введите смещение лет: +1 -увеличить на один, -1 уменьшить на один, 1 фиксирования цыфра',
        default='0',
    )

    def __str__(self):
        if len(self.name) > 150:
            return self.name[:150] + '...'
        return self.name

    class Meta:
        verbose_name = 'Шаблон задачи'
        verbose_name_plural = 'Шаблоны задач'


class Task(models.Model):
    """Модель с рабочими задачами"""
    pattern_task = models.ForeignKey(PatternTask,
                                     on_delete=models.PROTECT,
                                     verbose_name='Шаблонная задача',
                                     )
    plan = models.ForeignKey(Plan,
                             on_delete=models.CASCADE,
                             verbose_name='План-график',
                             )
    name = models.TextField(verbose_name='Имя задачи')
    completion_date = models.DateField(verbose_name='Дата выполнения')
    is_active = models.BooleanField(verbose_name='Активная?', default=True)
    perfomer = models.ForeignKey(Perfomer, on_delete=models.PROTECT, verbose_name='Исполнитель')
    user_creator = models.ForeignKey(UserDeteil,
                                     on_delete=models.PROTECT,
                                     verbose_name='Создатель',
                                     related_name='task_creator',
                                     )
    user_updater = models.ForeignKey(UserDeteil,
                                     on_delete=models.PROTECT,
                                     verbose_name='Последний редактор',
                                     related_name='task_updater',
                                     )
    date_of_creation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_update = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        if len(self.name) > 150:
            return self.name[:150] + '...'
        return self.name

    def get_absolute_url(self):
        return reverse('plans:task_detail', kwargs={'pk': self.id})

    def delete(self, *args, **kwargs):
        #TODO Нужно будет переделать метод удаления исполнителей
        super().delete(*args, **kwargs)
        Perfomer.objects.filter(~Q(id__in=Subquery(Task.objects.values('perfomer_id')))).all().delete()

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
