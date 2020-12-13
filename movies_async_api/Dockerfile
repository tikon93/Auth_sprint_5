FROM python:3.9.0-buster
#seems like alpine 3.12 has issues with rust toolchain installation

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app:${PYTHONPATH}

COPY ./requirements ./requirements
RUN python -m pip install -r requirements/common.txt --no-cache-dir

COPY ./api ./api
COPY ./core ./core
COPY ./db ./db
COPY ./models ./models
COPY ./services ./services
COPY ./tests ./tests
COPY ./main.py .

EXPOSE 8000/tcp

CMD ["python", "main.py"]
