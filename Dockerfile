FROM python:3.9-alpine3.15

RUN addgroup -S python && adduser -u 999 -S python -G python


RUN mkdir /usr/app && chown python:python /usr/app
WORKDIR /usr/app

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY --chown=python:python src src


USER 999

WORKDIR /usr/app/src
CMD ["python","cleaner.py"]
