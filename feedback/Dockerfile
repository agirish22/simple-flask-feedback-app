FROM python:3.9

COPY requirements.txt ./

RUN set -ex; \
    pip install -r requirements.txt; \
    pip install gunicorn

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
