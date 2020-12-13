FROM python:3.9.0-alpine3.12

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app:${PYTHONPATH}

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY ./requirements ./requirements
RUN python -m pip install -r requirements/base.txt --no-cache-dir && apk --purge del .build-deps

COPY ./movies ./movies
COPY ./config ./config
COPY ./manage.py .

EXPOSE 8000/tcp

# DJANGO_SETTINGS_MODULE shoud be used to set settings to run on, will be defaulted to dev
CMD ["python", "manage.py", "runserver"]
