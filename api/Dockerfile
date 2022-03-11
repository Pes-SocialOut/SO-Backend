FROM python:3.8-alpine

# Copiar nuestro fichero de dependencias
COPY ./requirements.txt /tmp/requirements.txt

# Actualizar pip y instalar dependencias
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt

# Copiar el código de nuestra app para que se pueda ejecutar
COPY ./run.py /api/run.py
COPY ./config.py /api/config.py
COPY ./app /api/app

EXPOSE 5000
WORKDIR /api
CMD ["python3", "run.py"]