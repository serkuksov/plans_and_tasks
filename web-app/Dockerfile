FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

RUN mkdir -p /home/app
RUN mkdir /home/app/web
RUN mkdir /home/app/staticfiles

WORKDIR /home/app/web

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

#RUN sed -i 's/\r$//g' /home/app/web/entrypoint.sh
#RUN chmod +x /home/app/web/entrypoint.sh

#RUN addgroup -S app && adduser -S app -G app
#RUN chown -R app:app ./
#
#USER app

#ENTRYPOINT ["/home/app/web/entrypoint.sh"]