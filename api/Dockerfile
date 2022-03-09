FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

# Copiar nuestro fichero de dependencias
COPY ./requirements.txt /tmp/requirements.txt

# Actualizar pip y instalar dependencias
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

# Copiar el código de nuestra app para que se pueda ejecutar
COPY ./run.py /api/run.py
COPY ./config.py /api/config.py
COPY ./app /api/app

WORKDIR /api
CMD ["python3", "run.py"]