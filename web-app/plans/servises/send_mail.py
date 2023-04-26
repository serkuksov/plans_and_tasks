from django.conf import settings
from django.core.mail import send_mail


def test_send_mail(emails: list) -> None:
    send_mail('Тема', 'Тело письма', settings.EMAIL_HOST_USER, emails)


if __name__ == '__main__':
    #Тест отправки писем
    import config.settings
    test_send_mail(['ser.kuksov@mail.ru'])
