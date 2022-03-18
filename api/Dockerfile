FROM python:3.8-slim

# Copiar nuestro fichero de dependencias
COPY ./requirements.txt /tmp/requirements.txt

# Actualizar pip y instalar dependencias
RUN pip install -U pip wheel
RUN pip install -r /tmp/requirements.txt

# Copiar el código de nuestra app para que se pueda ejecutar
COPY ./run.py /api/run.py
COPY ./config.py /api/config.py
COPY ./app /api/app

COPY ./docker-entrypoint.sh /api/docker-entrypoint.sh
COPY ./migrations /api/migrations
COPY ./manage.py /api/manage.py

WORKDIR /api
#FIXME: For some reason the env. var. don't get copied as they should
CMD ["python3", "run.py"]