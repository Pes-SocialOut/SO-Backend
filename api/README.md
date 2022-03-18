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

-- Upgrade de pip y wheel e instalar dependencias del proyecto
$: pip install -U pip wheel
$: pip install -r api/requirements.txt

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

Si te salen errores en docker que hablan sobre "Environmental variable is not set" hace falta exportar las variables de entorno a tu ordenador para que docker-compose las pueda encontrar.

Si estás en linux eres un máquina y es muy fácil:
```
$: source api/testEnv.sh
```
Si ejecutas lo siguiente y sale 5000 es que lo tienes bien:
```
$: echo $API_PORT
```
Deberías poder ejecutar el docker-compose y que funcionase.

En windows hay que ejecutar en el terminal de vscode (o PowerShell):
```
$: .\api\testEnvWin.ps1
```
Si salen errores en rojo sobre no poder ejecutar scripts es normal, pero habia que probar a ver si colaba ;)
Abre un PowerShell (no funciona en el terminal) en modo administrador! y ves al directorio del proyecto (SO-Backend):
```
$: Set-ExecutionPolicy -ExecutionPolicy Unrestricted
$: .\api\testEnvWin.ps1
$: Set-ExecutionPolicy -ExecutionPolicy Default
```
(devuelvo el modo a default por seguridad)
Para ver si ha funcionado ejecuta lo siguiente y deberia salirte un 5000
```
$: echo $Env:API_PORT
```
Vuelve a ejecutar la instrucción del docker y pásalo bien fiera.

Tras la primera ejecución, si la receta del Dockerfile o el docker-compose.yml no se cambia, no hace falta poner el flag de --build.

Para resetear el entorno podemos parar el container con:
```
$: docker-compose down -v
```
(Note: el flag -v elimina los volumenes, que són espacios de memoria del contenedor que se almacenan localmente. Si el servicio no usa volumenes no hace falta el flag)

Una vez esté corriendo deberias poder entrar a localhost:5000 en tu navegador y que te responda algo.

## EJECUTAR LA BD EN ENTORNO AISLADO
Los scripts de variables de entorno que has ejecutado antes también sirven para esta parte.

Ejecuta:
```
$: docker-compose up --build db
```
(recuerda lo del flag --build, solo la primera vez o si cambia la receta)

La base de datos PostgreSQL deberia estar corriendo!
Puedes conectarte a través de un cliente como por ejemplo DBeaver con las credenciales:
- username: socialout
- password: password1
- database: socialout
- port: 5432

En todo caso, para poner al dia la bd con la versión más reciente entra en el virtual environment de python (créalo como se indica más arriba si no lo has hecho aún) y ejecuta **des del directorio /api**:
```
$: python3 manage.py db migrate
```
Esto crea las versiones de migraciones (solo tiene efecto si has cambiado algo en los models.py de los módulos que están activamente en uso en la API).
Para trasladar estas actualizaciones a la bd:
```
$: python3 manage.py db upgrade
```
Mira con el DBeaver si se han creado las tablas que esperabas en tu PotsgreSQL.

***Cuidado!*** Si estás en Windows pero usas el WSL para correr el virtualenv y quieres hacer "migrate" o "upgrade" debes de correr el script testEnv.sh dentro del WSL para que la construcción de la API funcione, y también el testEnvWin.ps1 para que el docker coja las variables de entorno que necesita (al correr sobre Windows).

**NOTA:** Podeis ejecutar ambos entornos a la vez con:
```
$: docker-compose up --build
```
(sin el flag a partir de la segunda vez)