# IngSoftwareProyecto

## 1. Visión General del Proyecto

### 1.1. Propósito y Alcance
El Sistema de Gestión Clínica "Club Entre Patitas" es una aplicación web desarrollada para centralizar y administrar de manera eficiente la información de pacientes, fichas clínicas y atenciones médicas de una clínica veterinaria. El proyecto, en su versión actual, cubre integralmente los 11 casos de uso definidos en la fase de análisis, proveyendo una solución robusta para la gestión de datos y auditoría.

### 1.2. Arquitectura y Tecnologías
El sistema está construido sobre una arquitectura monolítica que garantiza un desarrollo ágil y un mantenimiento simplificado. Las tecnologías clave utilizadas son:

Backend: Framework Django (Python), que proporciona una estructura robusta para el desarrollo web rápido y seguro.

Base de Datos: SQLite, una base de datos ligera y basada en archivos, ideal para el desarrollo y el despliegue de aplicaciones de esta escala.

Frontend: Plantillas HTML renderizadas por el servidor, con estilos aplicados a través del framework Bootstrap 5 para una interfaz limpia, moderna y responsiva.

Auditoría: Paquete django-simple-history para el seguimiento automático y detallado de los cambios en los datos.

## 2. Guía de Instalación y Puesta en Marcha
Esta guía detalla los pasos necesarios para configurar y ejecutar el proyecto en un entorno de desarrollo local.

### 2.1. Requisitos Previos
Python 3.8 o superior.

pip (gestor de paquetes de Python).

Git (opcional, para clonar el repositorio).

### 2.2. Pasos de Instalación
Obtener el Código Fuente:
Crea una carpeta para el proyecto y descarga o clona el código fuente en ella. (dentro de algún idle como Visual Studio Code abrir la carpeta donde se encuentra almacenado el software)

Crear y Activar un Entorno Virtual:
Es una práctica recomendada aislar las dependencias del proyecto. Desde la carpeta raíz del proyecto, ejecuta:

#### Crear el entorno virtual
python -m venv venv

#### Activar en Windows
.\venv\Scripts\activate

#### Activar en macOS/Linux
source venv/bin/activate

Una vez activado, verás (venv) al principio de la línea de tu terminal.

En caso de tener algún problema sobre los permisos de ejecución, utilice esto:

Set-ExecutionPolicy RemoteSigned -Scope Process

Instalar las Dependencias:
Crea un archivo llamado requirements.txt en la raíz del proyecto con el siguiente contenido:

Django>=4.0
django-simple-history

Luego, instala estas dependencias ejecutando:

pip install -r requirements.txt

o seguir estas instrucciones mas basicas:

pip install django (para instalar las dependencias de django)
pip install django-simple-history

para saber si esta instalado correctamente Django usar:

pip freeze

Aplicar las Migraciones de la Base de Datos:
Este comando creará el archivo de base de datos (db.sqlite3) y todas las tablas necesarias según los modelos definidos.

python manage.py migrate

Crear un Superusuario Administrador:
Este usuario tendrá acceso a todas las funcionalidades y al panel de administración de Django.

python manage.py createsuperuser

Sigue las instrucciones para crear tu nombre de usuario, correo (opcional) y contraseña.

Ejecutar el Servidor de Desarrollo:
¡Todo está listo para ejecutar la aplicación!

python manage.py runserver

El sistema estará disponible en tu navegador en la dirección http://127.0.0.1:8000/.

Las direcciones explicadas son:

http://127.0.0.1:8000 ==> lleva directamente a la pagina del portal de club entre patitas

http://127.0.0.1:8000/admin ==> lleva directamente a la pagina donde esta la base de datos (se ingresa con las credenciales de superuser)

## 3. Funcionalidades Implementadas
El sistema cuenta con las siguientes funcionalidades principales, cubriendo todos los casos de uso definidos:

Portal de Bienvenida y Autenticación:

Una página de bienvenida que sirve como punto de entrada.

Un sistema de inicio de sesión seguro (/accounts/login/) para proteger el acceso a la información. Solo los usuarios autenticados pueden operar en el sistema.

Actualmente el usuario:contraseña que hay es:
 
admin:adminadmin (porque es el superuser creado)
Veterinario:TAqi4d6ygQi5vxG (único usuario creado de acceso)

Gestión Integral de Pacientes (CRUD):

Crear: Formulario para registrar nuevos pacientes con sus datos básicos y asociarlos a un tutor (totores ya creados para prueba).

Leer: Listado completo de pacientes con una interfaz limpia y paginada.

Actualizar: Formulario de edición para modificar la información de un paciente existente.

Borrar: Flujo de eliminación con página de confirmación para evitar borrados accidentales.

Gestión de Ficha Clínica Detallada:

Atenciones Médicas (CRUD): Posibilidad de crear, editar y borrar atenciones para cada paciente.

Chequeo Físico: Formulario integrado para registrar datos específicos como temperatura, peso y condición corporal en cada atención.

Anamnesis y Motivo de Consulta: Campos dedicados para registrar el historial y la razón de la visita.

Clasificación de Atención: Selector para diferenciar si la atención fue en la "Clínica" o en el "Club".

Selección de Tipos de Ficha (General y Hospitalización):

Flujo de trabajo que permite al veterinario elegir entre registrar una "Consulta General" o una "Hospitalización", presentando formularios adaptados con campos adicionales para el caso de hospitalización.

Registro de Procedimientos:

Funcionalidad para añadir múltiples procedimientos (exámenes, cirugías, etc.) a una atención médica existente, con detalles y fechas.

Búsqueda Avanzada:

Un formulario de búsqueda en la lista de pacientes que permite filtrar por nombre, diagnóstico o fecha de atención, facilitando la localización de información.

Sistema de Auditoría y Trazabilidad:

Registro Automático: Cada modificación en una atención médica queda registrada automáticamente con fecha, hora y usuario (Caso de Uso 10).

Bitácora de Cambios: Interfaz de "Historial" para cada atención, donde un usuario autorizado puede consultar todos los cambios realizados sobre ese registro (Caso de Uso 11).
