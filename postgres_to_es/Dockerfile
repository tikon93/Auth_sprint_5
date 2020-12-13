FROM python:3.9.0-alpine3.12

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app/src:${PYTHONPATH}

RUN \
 apk add --no-cache postgresql-libs linux-headers && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir && apk --purge del .build-deps

COPY ./src ./src
COPY ./postgres_to_es.py .

CMD ["python", "postgres_to_es.py"]
