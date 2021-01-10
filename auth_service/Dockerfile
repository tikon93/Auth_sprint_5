FROM python:3.9.0-buster

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app:${PYTHONPATH}
ENV FLASK_APP=/opt/app/app.py

COPY ./requirements ./requirements
RUN python -m pip install -r requirements/common.txt --no-cache-dir

COPY ./src ./src
COPY ./migrations ./migrations
COPY ./app.py .
COPY ./manage.py .

EXPOSE 5000/tcp

CMD ["python", "app.py"]
