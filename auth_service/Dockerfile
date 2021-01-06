FROM python:3.9.0-buster

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app:${PYTHONPATH}
ENV FLASK_APP=/opt/app/app.py

COPY ./requirements.txt ./requirements.txt
RUN python -m pip install -r requirements.txt --no-cache-dir

COPY ./src ./src
COPY ./app.py .

EXPOSE 5000/tcp

CMD ["python", "app.py"]