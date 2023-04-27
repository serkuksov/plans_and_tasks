from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse

from accounts.models import UserDeteil
from plans import models
from ..tasks import task_send_mail
from config.celery import app


def test_send_mail(emails: list) -> None:
    send_mail('Тема', 'Тело письма', settings.EMAIL_HOST_USER, emails)


@app.task()
def notify_manager_plan_creation(plan_id: int) -> None:
    """Отправка уведомления по электронной почте о создании нового плана
    начальникам структурных подразделений фигурирующих в плане"""
    subject = 'Создание нового плана'
    message = f'Создан новый план-график по которому вам необходимо назначить исполнителей. ' \
              f'Ссылка на план: {reverse("plans:plan_detail", kwargs={"pk": plan_id})}'
    task_send_mail.apply_async(kwargs={'subject': subject,
                                       'message': message,
                                       'recipient_list': get_email_manager_plan(plan_id=plan_id)})


def notify_manager_plan_delete():
    """Отправка уведомления по электронной почте об удалении плана
    начальникам структурных подразделений фигурирующих в плане"""
    pass


def notify_plan_creation():
    """Отправка уведомления по электронной почте о создании нового плана
    начальникам структурных подразделений фигурирующих в плане"""
    pass


def notify_worker_assignment():
    """Отправка уведомления по электронной почте работнику о
    назначении его исполнителем по задаче"""
    pass


def notify_worker_remove_assignment():
    """Отправка уведомления по электронной почте работнику о
    снятии функции исполнителя по задаче"""
    pass


def notify_task_due_date_approaching():
    """Отправка уведомления по электронной почте работнику и начальнику о
    приближении даты выполнения задачи"""
    pass


def get_email_manager_plan(plan_id: int) -> list[str]:
    """Функция возвращает список email менеджеров подразделений учавтвующих в решении задач плана"""
    email_users = list(get_user_model().objects.
                       filter(userdeteil__division__perfomer__task__plan_id=plan_id, userdeteil__is_manager=True).
                       distinct().
                       values_list('email', flat=True)
                       )
    return list(filter(lambda x: x.strip(), email_users))


    # from django.db import connection
    #
    # queries = connection.queries
    # for query in queries:
    #     print(query)



if __name__ == '__main__':
    # Тест отправки писем
    import config.settings

    test_send_mail(['ser.kuksov@mail.ru'])
