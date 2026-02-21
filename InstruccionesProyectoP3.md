#objetivo:

Continuamos trabajando en el proyecto de generación de tareas a partir de historias de usuario. En este entregable, el objetivo es completar el desarrollo de la aplicación con interfaz de usuario y base de datos. Para ello, conectarás la aplicación FasApi a base de datos relacional MySQL y utilizarás salidas estructuradas de IA para almacenar resultados y mostrarlos por la interfaz de usuario.

Tomando como base el proyecto actual, maneteniendo las funcionalidades y directrices escritas en los archivos 'agents.md', 'InstruccionesProyecto.md' y 'InstruccionesProyecto2.md', se debe agregar las siguientes fucnonalidades:

# Crear la estructura de carpetas y proyecto necesaria para tener una conexion a base de datos .
# La conexión a base de datos MySQL y los settings de conexion deben leerse y cargarse de un archivo de configuracion llamado 'settingsApp.json'.
# refinar la separacion de servicios. en el proyecto.
# los esquemas relacionados con base de datos deben ser con Pydantic para manejar todo en formato json.
#	Generación de Schemas con Pydantic:
- UserStorySchema.
- UserStorySchemas.
- TaskSchema.
- TaskSchemas.
- En este cso se debe trasladar la estructura, datos y logica en general de 'category'(archivo 'tasks_json.json') a una tabla de base de datos Mysql 
- En este caso se busca pasar la logica del manejo de 'task' del proyecto a una base de datos con todas las modificaciones que esto implique para que el proyecto mantenga las funcionalidades anteriores pero almacenando los datos en DB de mySql.
# Generación de modelos SQLAlchemy:
UserStory con campos:
•	id (primary key).
•	project (nombre de proyecto).
•	role (rol de usuario en la historia).
•	goal (objetivo de la historia de usuario).
•	reason (razón de la historia de usuario).
•	description (texto largo que describe en qué consiste toda la historia de usuario).
•	priority (prioridad baja, media, alta, bloqueante).
•	story_points (puntos de historia estimados 1-8).
•	effort_hours (número decimal, horas estimadas para completar la historia).
•	created_at (fecha creación se crea automática a nivel de base de datos).
•	Agregar más campos si se quiere.

Task
•	id (primary key).
•	title (título de la tarea).
•	description (texto largo que describe completamente la tarea).
•	priority (prioridad baja, media, alta, bloqueante).
•	effort_hours (número decimal, horas estimadas para completar la historia).
•	status (estado pendiente, en progreso, en revisión, completada).
•	assigned_to (string, persona del equipo a la que se asigna).
•	user_story_id (asociación many to one con UserStory).
•	created_at (fecha creación se crea automática a nivel de base de datos).
•	Agregar más campos si se quiere.

# Generación de endpoints mvc:
- GET  /user-stories: que devolverá un HTML user-stories.html, donde se verán todas las historias de usuario y tendrá una textarea para escribir prompt para enviar a backend para solicitar generar historias de usuario a partir del prompt. Mostrará un listado con todas las historias de usuario existentes en base de datos. Cada historia de usuario tendrá un botón «Generar tareas», que al pulsarlo llamará a otro endpoint.

- POST /user-stories: al que se envía el formulario de user-stories.html, extrae el prompt y lo usa para generar una historia de usuario completa y almacenarla en base de datos.

- POST /user-stories/{id}/generate-tasks: este endpoint es el que se invoca cuando se pulsa el botón de generar tareas sobre una historia de usuario. Aquí se generan las tareas para esa historia de usuario usando IA y se almacenan en base de datos asociadas a la historia de usuario. Tras ello se vuelve a mostrar la pantalla de tasks.html en una URL GET /user-stories/{id}/tasks, donde se verían las tareas de esa historia de usuario. 

# Para cualquier salida de un endpoint que sea un HTML, esta debe ser una plantilla alnacenada en una carpeta llmada 'templates' y debe ser con jinja y Bootstrap, en este caso se debe mantener una apariencia con tonos grises usando CSS.

# debido a que ya no se requiere el archivo 'tasks_json.josn este debe ser eliminado junto con la carpeta 'data'.
# crear reositorio en git
# actualizar documentacion del archivo readme.md
#  Agregar los test en pythest para los cambios realizados.
