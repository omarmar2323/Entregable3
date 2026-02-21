#objetivo:

Tomando como base el proyecto actual, maneteniendo las funcionalidades y directrices escritas en los archivos 'agents.md' y 'InstruccionesProyecto.md', se debe agregar las siguientes fucnonalidades:


1. Nuevos campos para el modelo Task:
- id 
- title
- description
- priority
- effort_hours
- status
- assigned_to
- category --> Nuevo campo puede ser str o enum
- risk_analysis --> Nuevo campo texto
- risk_mitigation --> Nuevo campo texto

2. Nuevos endpoints.

Conservamos los endpoints CRUD ya existentes y agregamos nuevos endpoints, que serán:

- POST /ai/tasks/describe

recibe una task con description vacía y genera su description con LLM a partir del resto de campos como el title. Este endpoint podría devolver la misma tarea que ha recibido pero con el campo description relleno.

- POST /ai/tasks/categorize

recibe una tarea sin categoría y con LLM debe poder clasificarla bajo una categoría: Frontend, Backend, Testing, Infra, etc. Este endpoint podría devolver la misma tarea que ha recibido pero con el campo category relleno.

-	POST /ai/tasks/estimate

recibe una tarea sin effort_hours y con LLM debe poder estimar su esfuerzo en horas leyendo su title, description y category. Este endpoint podría devolver la misma tarea que ha recibido pero con el campo effort_hours relleno, importante, es un campo numérico no de texto, por lo que habrá que hacer parsing.

- POST /ai/tasks/audit

recibe una tarea con todos los campos rellenos menos risk_analysis y risk_mitigation. Con esa tarea utiliza sus datos para lanzar dos peticiones a un LLM. Una primera petición para obtener un análisis de riesgos que puedan surgir en la tarea y almacenarlo en risk_analysis y una segunda petición que use esa info junto a la de la tarea para pedir un plan de mitigación de riesgos que se almacene en risk_mitigation.

3. Integracion del LLM:

* El proyecto debe usar la libreria OpenAI para la conexion con LLMs de azure.

* EL proyecto debe poder personalizar las interacciones del LLM ajustando los parámetros de comportamiento (temperature, max_tokens, top_p, etc.). Estos parametros edbe estar en un archivo de configuraciion llamado llm_settings.json el cual debe ser leido y cargado para ser usado en las interaccion con el modelo de lenguaje.

* el archivo llm_settings.json contendrá adicionalmente los settings necesarios para crear una conexión con OpenAI, en este archivo debe estar el endpoint, deployment_name y api_key.

* Debe partir del listado 'Frontend, Backend, Testing, Infra' y adicionar mas categorias que este relacionadas con un emresa de tecnologia, como minimo deben ser 10 y quedar incluidas en el archivo 'tasks_json.json' como una lista con el nombre 'category'.

* El archivo llm_settings.json debe tener la configuracion del rol 'system' los siguientes parametros de comportamiento:
  - Cuando se pida una 'description' esta no debe superar los 200 palabras.
  - Cuando se pida un analisis de riesto 'risk_analysis', la respuesta no debe superaar las 200 palabras y para la mitigacion del riesgo 'risk_mitigation' no debe superar las 300 palabras.
  - Actua como un manager y experto en desarrollo de software e infraestructura. 
  - Actua como un experto en gestion de proyecto de softwrae.
  - Actua como un experto arquietectura de software.

4. Se deben agregar los respectivos tests para las nuevas funcionalidades.

5. Inicializar el repositorio con git y en caso de que encuentres ya alguna referencia a un repositorio antiguo, borralo y genera uno nuevo.

6. Se actualizar la documentacion de las nuevas funcionalidades en el archivo readme que incluya ejemplos de uso.

7. se debe actualizar el archivo de 'requirements.txt'.






