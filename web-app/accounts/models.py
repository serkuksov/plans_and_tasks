from django.db import models
from django.contrib.auth import get_user_model
from django.core import validators


class Division(models.Model):
    name = models.CharField(max_length=15, verbose_name='Название подразделения')
    parent_division = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='Вышестоящее подразделение', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'



class UserDeteil(models.Model):
    """Дополнение модели пользователя"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    second_name = models.CharField(max_length=20, verbose_name='Отчество', blank=True)
    phone_number = models.PositiveSmallIntegerField(verbose_name='Номер телефона', blank=True,
                                                    unique=True,
                                                    validators=[validators.MinValueValidator(3200), 
                                                                validators.MaxValueValidator(3399)])
    division = models.ForeignKey(Division, on_delete=models.PROTECT, verbose_name='Подразделение', null=True, blank=True)
    is_manager = models.BooleanField(verbose_name='Руководитель?', default=False)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return f'{self.user.last_name} {self.user.first_name} {self.second_name}'

    class Meta:
        verbose_name = 'Дополнительные данные пользователя'
        verbose_name_plural = 'Дополнительные данные пользователей'



    