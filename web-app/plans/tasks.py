import time

from django.core.mail import send_mail
from django.conf import settings
from config.celery import app


@app.task()
def test_task():
    print('-' * 10)
    time.sleep(5)
    print('+' * 10)
    return True


@app.task(bind=True)
def task_send_mail(self, subject: str, message: str, recipient_list: list) -> None:
    """Функция рассылки по электронной почте с использованием celery"""
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
    except Exception as exc:
        # повторная попытка выполнения задачи
        self.retry(exc=exc, countdown=60, max_retries=2)

