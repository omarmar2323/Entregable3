#objetivo:

Vamos a crear un proyecto de generación de tareas que se asignan a usuarios. 
El objetivo es comenzar con el desarrollo de la aplicación FastAPI. 
Para ello, crearás una aplicación con FastAPI, organizando toda la arquitectura del 
proyecto creando rutas que conecten con los controladores para devolver resultados asociados a través de un json.

#Pautas de elaboración

Crea una aplicación FastAPI que tenga rutas y controladores para la gestión de tareas de usuario. 
Los campos de tareas tendrán el siguiente interfaz:
 
- Task
	 • id (primary key).
	 • title (título de la tarea).
	 • description (texto largo que describe completamente la tarea).
	 • priority (prioridad baja, media, alta, bloqueante).
	 • effort_hours (número decimal, horas estimadas para completar la tarea).
	 • status (estado pendiente, en progreso, en revisión, completada).
	 • assigned_to (string, persona del equipo a la que se asigna).

Nota1: las tareas seran almacenadas en la carpeta data en un archivo json llamado TasksJSON, el cual 
contiene las tareas(Tasks) en un diccionario de listas. La clave del diccionario de lsitas sera Tasks.

Nota2: La logica del 'id' se manejara como un campo independiente dentro del diccionario, el cual sera consultado 
y/o modificado cada vez que se cree una nueva tarea.


Generación de endpoints:

- Crear una tarea (POST /tasks).
- Leer todas las tareas (GET /tasks).
- Leer una tarea específica (GET /tasks/<id>).
- Actualizar una tarea (PUT /tasks/<id>).
- Eliminar una tarea (DELETE /tasks/<id>).

Crearás un fichero de rutas, donde darás de alta todas las rutas especificadas que 
llamarán a la clase TaskManager, que deberá gestionar el uso de tareas con el archivo json. 
También existirá un clase Task, que permitirá definir una tarea y convertirla en un diccionario para poder insertarla en un json.	

- Clase Task: representa una tarea con los datos del interfaz. 
Métodos:
•	to_dict(): convierte el objeto Task a diccionario.
•	from_dict(): crea un Task desde un diccionario.

- Clase TaskManager
Métodos estáticos:
•	load_tasks(): carga tareas desde tasks.json y las convierte en objetos Task.
•	save_tasks(): guarda la lista de Task en el archivo JSON.

FastAPI
•	GET /tasks → devuelve todas las tareas.
•	GET /tasks/ → devuelve una tarea específica.
•	POST /tasks → crea una tarea nueva.
•	PUT /tasks/ → modifica una tarea existente.
•	DELETE /tasks/ → elimina una tarea.

# Pruebas del proyecto

Implementación de pruebas unitarias con la librería pytest:

-   Crear tarea.
-   Leer todas las tareas.
-   Leer una tarea específica.
-   Actualizar una tarea.
-   Eliminar una tarea


# Documentación del proyecto

Generar un README que incluya:

-   Objetivo del proyecto.
-   Instrucciones de instalación y ejecución.
-   Ejemplo de uso.
