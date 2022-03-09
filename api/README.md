## ESTRUCTURA DE FICHEROS DE LA API

En api/config.py hay la configuración de la app flask.
En api/run.py hay la ejecución trivial de la app flask.
En el directorio app hay:
    - __init__.py que se ejecuta automáticamente al importar /app en run.py
    - Para cada módulo / servicio en el que podamos dividir la api habrá un directorio.

En un directorio de módulo habrá básicamente dos ficheros:
- controllers.py : Define las rutas de la api que controla ese módulo
- models.py : Define unos metamodelos de tablas que queramos persistir con sqlalchemy

(Note: En el primer commit no hay nada implementado de BD por lo que tener estos metamodelos ahora no aporta mucho. La idea es usar el sqlalchemy de flask + postgres)


## ENTORNO VIRTUAL DE LA API

Si hay que instalar librerías de python para ejecutar tests o pruebas en local, ejecutar des del directorio base de proyecto:

```
$: python3 -m venv api/env

-- Activa el entorno virtual de trabajo
$: source api/env/bin/activate

-- Instalar dependencias antiguas
$: pip install api/requirements.txt

-- Instalar nuevas dependencias
$: pip install ...[librerías a añadir]...

-- Hacer tests, pruevas, etc.

-- Guardar nuevas dependencias en requirements para que los demás las tengan al proximo "pull"
$: pip freeze > api/requirements.txt

-- Desactivar el entorno
$: deactivate
```

## EJECUTAR LA API LOCALMENTE

Primero instala los requirements.txt como se explica arriba.
```
-- Ejecuta con el entorno activo:
$: python3 api/run.py

-- o bien, ejecuta sin el entorno activo:
$: api/env/bin/python3 api/run.py
```

## EJECUTAR LA API EN ENTORNO AISLADO

Instala el Docker desktop de tu sistema operativo.
Si trabajas en Windows, tras instalarlo y abrirlo te pedirá que instales WSL2 (Windows Subsystem Linux) que básicamente es una VM de ubuntu que corre en windows.
Cuando en la ventana de docker, la barrita de abajo a la izquierda con el logo de docker esté en verde, querrá decir que has hecho bien la instalación y puedes continuar.

La primera vez que vayas a ejecutar un contenedor (en este caso el de api):
```
$: docker-compose up --build api
```
(Note: Si estás en windows ejecutalo des del terminal que se abre en el VSCode, no hace falta entrar en wsl)

Tras la primera ejecución, si la receta del Dockerfile o el docker-compose.yml no se cambia, no hace falta poner el flag de --build.

Para resetear el entorno podemos parar el container con:
```
$: docker-compose down -v
```
(Note: el flag -v elimina los volumenes, que són espacios de memoria del contenedor que se almacenan localmente. Si el servicio no usa volumenes no hace falta el flag)

Una vez esté corriendo deberias poder entrar a localhost:5000 en tu navegador y que te responda algo.