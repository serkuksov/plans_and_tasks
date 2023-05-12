import datetime
from calendar import monthrange

from dateutil.relativedelta import relativedelta
from workalendar.europe import Russia


def add_date_delta(date: datetime.datetime, days: int, months: int, years: int) -> datetime.datetime:
    """Добавить к дате смещение на заданое количество дней, месяцев, лет"""
    return date + relativedelta(days=days, months=months, years=years)
 

def get_ofset_params_date(days: str, months: str, years: str) -> dict:
    """Преобразовать строковое предстовление смещения полученое в виде аргументов со знаками + и - в цыфровое.
    В случае отсутствия у аргумента арефметического символа присвоить смещению значение 0.
    Возвращает словарь с ключами days: int, months: int, years: int"""
    return {
        'days': get_ofset_number(days),
        'months': get_ofset_number(months),
        'years': get_ofset_number(years),
    }


def get_ofset_number(ofset_number: str) -> int:
    """Преобразует строку в число по принцыпу наличия арефметического символа"""
    if '+' in ofset_number or '-' in ofset_number:
        return int(ofset_number)
    else:
        return 0


def get_fixed_params_date(days: str, months: str, years: str) -> dict:
    """Преобразовать строковое предстовление фиксированой даты
    полученое в виде строкового представления числа без ареф аргументов.
    В случае наличия у аргумента арефметического символа присвоить фиксированой дате значение 0.
    Возвращает словарь с ключами days: int, months: int, years: int"""
    return {
        'days': get_fixed_number(days),
        'months': get_fixed_number(months),
        'years': get_fixed_number(years),
    }


def get_fixed_number(ofset_number: str) -> int:
    """Преобразует строку в число по принцыпу отсутствия арефметического символа"""
    if '+' in ofset_number or '-' in ofset_number:
        return 0
    else:
        return int(ofset_number)


def set_fixed_args_date(date: datetime.datetime, days: int, months: int, years: int) -> datetime.datetime:
    """Устанавливает постоянные атрибуты даты.
    Если значение фиксированого дня больше количества дней в месяце выставляется последний день месяца"""
    if months > 0:
        date = date.replace(month=months)
    if years > 0:
        date = date.replace(year=years)
    if days > 0:
        _, count_days = monthrange(year=date.year, month=date.month)
        if days > count_days:
            date = date.replace(day=count_days)
        else:
            date = date.replace(day=days)
    return date


def get_data_with_working_day(date: datetime.datetime) -> datetime.datetime:
    """Возвращает переданую дату или дату последнего
    предшествующего рабочего дня если попало на выходные"""
    cal = Russia()
    while not cal.is_working_day(date):
        date -= datetime.timedelta(days=1)
    return date


def get_completion_date_for_task(completion_date: datetime.datetime,
                                 days: str,
                                 months: str,
                                 years: str) -> datetime.datetime:
    """Выдает дату завершения выполнения задачи на
    основе даты завершения плана и параметров смещения"""
    completion_date_for_task = add_date_delta(date=completion_date, **get_ofset_params_date(days, months, years))
    completion_date_for_task = set_fixed_args_date(date=completion_date_for_task, **get_fixed_params_date(days, months, years))
    completion_date_for_task = get_data_with_working_day(date=completion_date_for_task)
    return completion_date_for_task
