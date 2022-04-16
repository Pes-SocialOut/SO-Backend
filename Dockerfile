FROM python:3.8-slim

# Copiar nuestro fichero de dependencias
COPY ./requirements.txt /tmp/requirements.txt

# Actualizar pip y instalar dependencias
RUN pip install -U pip wheel
RUN pip install -r /tmp/requirements.txt

# Copiar el código de nuestra app para que se pueda ejecutar
COPY ./run.py /wsgi.py
COPY ./config.py /config.py
COPY ./app /app

WORKDIR /
CMD ["python3", "wsgi.py"]