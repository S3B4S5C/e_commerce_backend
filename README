# E-Commerce Backend

Este proyecto es un backend para una aplicación de comercio electrónico. A continuación, se detallan las instrucciones para instalar las dependencias necesarias y ejecutar el proyecto.

## Requisitos previos

Asegúrate de tener instalados los siguientes programas en tu sistema:

- [Python](https://www.python.org/) (versión 3.8 o superior)
- [pip](https://pip.pypa.io/) (gestor de paquetes de Python)
- [PostgreSQL](https://www.postgresql.org/) (base de datos)

## Instalación

1. Clona este repositorio en tu máquina local:

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd e_commerce_backend
    ```

2. Crea y activa un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3. Instala las dependencias del proyecto:

    ```bash
    pip install -r requirements.txt
    ```

4. Configura las variables de entorno:

    Crea un archivo `.env` en la raíz del proyecto y define las siguientes variables:

    ```
    SECRET_KEY=tu_secreto
    DEBUG=True
    DATABASE_URL=postgres://usuario:contraseña@localhost:5432/e_commerce
    ```

5. Realiza las migraciones de la base de datos:

    ```bash
    python manage.py migrate
    ```

## Ejecución del proyecto

1. Asegúrate de que PostgreSQL esté corriendo en tu máquina local.

2. Inicia el servidor de desarrollo:

    ```bash
    python manage.py runserver
    ```

3. El servidor estará disponible en `http://127.0.0.1:8000`.

## Scripts disponibles

- `runserver`: Inicia el servidor de desarrollo.
- `migrate`: Aplica las migraciones de la base de datos.
- `createsuperuser`: Crea un usuario administrador para el panel de Django.

## Dependencias principales

- `django`: Framework principal para el desarrollo del proyecto.
- `djangorestframework`: Herramientas para construir APIs REST.
- `psycopg2-binary`: Conector para interactuar con PostgreSQL.

## Contribuciones

Si deseas contribuir, por favor abre un issue o envía un pull request.

¡Gracias por usar este proyecto!
