import time

from config.celery import app


@app.task()
def test_task():
    print('-' * 10)
    time.sleep(5)
    print('+' * 10)
    return True
