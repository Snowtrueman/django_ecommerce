FROM python:3.10.10-alpine

WORKDIR /usr/src/app

RUN mkdir /usr/src/app/static
RUN mkdir /usr/src/app/media

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /home/app
RUN addgroup -S app && adduser -S app -G app

COPY . .

RUN chown -R app:app /usr/src/app

USER app

