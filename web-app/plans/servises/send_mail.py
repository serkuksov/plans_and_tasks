import datetime

from django.contrib.auth import get_user_model
from django.conf import settings

from ..models import Task
from ..tasks import task_send_mail
from config.celery import app


@app.task()
def notify_manager_plan_creation(plan_id: int, plan_url: str) -> None:
    """Отправка уведомления по электронной почте о создании нового плана
    начальникам структурных подразделений фигурирующим в плане"""
    subject = 'Создание нового плана'
    message = f'Создан новый план-график по которому вам необходимо выполнить редактирование задач. ' \
              f'Ссылка на редактирование задач: {plan_url}'
    task_send_mail.apply_async(kwargs={'subject': subject,
                                       'message': message,
                                       'recipient_list': get_email_manager_plan(plan_id=plan_id)})


def notify_manager_plan_delete(plan_id: int, plan_description: str) -> None:
    """Отправка уведомления по электронной почте об удалении плана
    начальникам структурных подразделений фигурирующих в плане"""
    subject = 'Удаление плана'
    message = f'Удален не актуалный {plan_description}.'
    recipient_list = get_email_manager_plan(plan_id=plan_id) + get_email_worker_plan(plan_id=plan_id)
    task_send_mail.apply_async(kwargs={'subject': subject,
                                       'message': message,
                                       'recipient_list': recipient_list})


def notify_worker_assignment(task_name: str, task_url: str, email_user: str) -> None:
    """Отправка уведомления по электронной почте работнику о
    назначении его исполнителем по задаче"""
    subject = 'Назначение исполнителем'
    message = f'Вы назначены исполнителем по задаче "{task_name}". ' \
              f'Ссылка на задачу: {task_url}'
    task_send_mail.apply_async(kwargs={'subject': subject,
                                       'message': message,
                                       'recipient_list': [email_user]})


def notify_worker_remove_assignment(task_name: str, email_user: str) -> None:
    """Отправка уведомления по электронной почте работнику о
    снятии функции исполнителя по задаче"""
    subject = 'Снятие функции исполнителя'
    message = f'С вас снята функция исполнителя по задаче "{task_name}".'
    task_send_mail.apply_async(kwargs={'subject': subject,
                                       'message': message,
                                       'recipient_list': [email_user]})


@app.task()
def notify_task_due_date_approaching(days: int) -> None:
    """Отправка уведомления по электронной почте работнику и начальнику о
    приближении даты выполнения задачи за N дней"""
    task_qs = (Task.objects.
               filter(completion_date=datetime.datetime.now().date() + datetime.timedelta(days=days),
                      is_active=True).
               select_related('perfomer__performer_user__user').
               all())
    print(task_qs)
    for task in task_qs:
        print(get_email_manager_and_worker_task(task_id=task))
        if days:
            subject = 'Уведомление по задаче'
            message = f'До даты исполнения задичи "{task.name}" осталось {days} дней. '
        else:
            subject = 'Срок исполнения по задаче'
            message = f'Сегодня дата исполнения задичи "{task.name}". '
        message += f'Ссылка на задачу: {get_current_host()}{task.get_absolute_url()}'
        task_send_mail.apply_async(kwargs={'subject': subject,
                                           'message': message,
                                           'recipient_list': get_email_manager_and_worker_task(task_id=task)})


def get_email_manager_plan(plan_id: int) -> list[str]:
    """Функция возвращает список email менеджеров подразделений учавтвующих в решении задач плана"""
    email_users = list(get_user_model().objects.
                       filter(userdeteil__division__perfomer__task__plan_id=plan_id, userdeteil__is_manager=True).
                       distinct().
                       values_list('email', flat=True)
                       )
    return list(filter(lambda x: x.strip(), email_users))


def get_email_manager_and_worker_task(task_id: int) -> list[str]:
    """Функция возвращает список email менеджера и исполнителя задачи"""
    email_manager = list(get_user_model().objects.
                       filter(userdeteil__division__perfomer__task=task_id, userdeteil__is_manager=True).
                       distinct().
                       values_list('email', flat=True)
                       )
    email_worker = list(get_user_model().objects.
                       filter(userdeteil__perfomer__task=task_id, userdeteil__is_manager=False).
                       distinct().
                       values_list('email', flat=True)
                       )
    return list(filter(lambda x: x.strip(), email_manager + email_worker))


def get_email_worker_plan(plan_id: int) -> list[str]:
    """Функция возвращает список email исполнителей учавтвующих в решении задач плана"""
    email_users = list(get_user_model().objects.
                       filter(userdeteil__perfomer__task__plan_id=plan_id, userdeteil__is_manager=False).
                       distinct().
                       values_list('email', flat=True)
                       )
    return list(filter(lambda x: x.strip(), email_users))

    # from django.db import connection
    #
    # queries = connection.queries
    # for query in queries:
    #     print(query)


def get_current_host() -> str:
    return f'http://{settings.ALLOWED_HOSTS[0]}:8000'
