# gestor_de_tareas_fastapi

**Versión**: 2.0.0 | **Estado**: ✅ Producción | **Fecha**: Febrero 2026

Aplicación FastAPI completa para la **gestión de tareas e historias de usuario** con base de datos MySQL, interfaz web MVC y generación de contenido con IA. 

## resumen_ejecutivo

🎯 **Proyecto evolucionado** de almacenamiento JSON a una aplicación empresarial completa:
- 🗄️ **Base de datos MySQL** con SQLAlchemy ORM
- 🌐 **Interfaz web HTML** con Jinja2 + Bootstrap 5.3
- 🤖 **Generación automática con IA** de historias de usuario y tareas técnicas
- 📊 **Arquitectura MVC** + API REST
- ✅ **14 archivos nuevos** | 3,500+ líneas de código | Cobertura completa de tests

## objetivo_del_proyecto

- Gestionar **historias de usuario** e **tareas** con interfaz web y base de datos MySQL
- Generar automáticamente historias de usuario y tareas usando **IA (Azure OpenAI)**
- Los datos incluyen:
  - **Historias de Usuario**: project, role, goal, reason, description, priority, story_points, effort_hours
  - **Tareas**: title, description, priority, effort_hours, status, assigned_to, category, risk_analysis, risk_mitigation
- Almacenamiento en **MySQL** con SQLAlchemy ORM
- Interfaz web con **Jinja2 + Bootstrap 5.3**

## estructura_del_proyecto

```text
project_root/
│── app/
│   ├── main.py                    # Aplicación FastAPI principal
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── tasks_router.py        # Endpoints CRUD /tasks
│   │   ├── ai_router.py           # Endpoints IA /ai/tasks/*
│   │   └── user_stories_router.py # Endpoints MVC /user-stories
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_manager.py        # (Legacy) Manejo de tareas
│   │   ├── task_service.py        # CRUD tareas en BD
│   │   ├── user_story_service.py  # CRUD historias en BD
│   │   ├── ai_user_story_service.py # Generación IA de historias/tareas
│   │   └── llm_service.py         # Cliente Azure OpenAI
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task_model.py          # Modelo Pydantic task
│   │   ├── task_schema.py         # Schemas Pydantic para BD
│   │   └── user_story_schema.py   # Schemas Pydantic historias
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py            # Conexión SQLAlchemy
│   │   └── models.py              # Modelos ORM (user_story, task)
│   └── core/
│       ├── __init__.py
│       ├── config.py              # Configuración desde settingsApp.json
│       └── llm_settings.json      # Credenciales Azure OpenAI
│
│── templates/
│   ├── user_stories.html          # Vista de historias de usuario
│   └── tasks.html                 # Vista de tareas
│
│── tests/
│   ├── __init__.py
│   ├── test_tasks_api.py          # Tests endpoints /tasks
│   ├── test_ai_endpoints.py       # Tests endpoints /ai/tasks/*
│   ├── test_user_stories_endpoints.py # Tests endpoints MVC
│   └── test_database_services.py  # Tests servicios BD
│
│── init_db.py                     # Script inicialización BD
│── settingsApp.json               # Configuración MySQL
│── requirements.txt
│── .gitignore
│── README.md
```

> Nota: el proyecto sigue estrictamente el estilo `snake_case` para clases, variables, métodos, archivos y carpetas.

## ubicacion_de_clases_y_servicios

### Modelos Pydantic (app/models/)

- **task** (`app/models/task_model.py`): Esquema Pydantic para tareas con validación estricta.
  - `to_dict()`: convierte la instancia a diccionario serializable.
  - `from_dict(data)`: crea una instancia desde diccionario.

- **task_ai_input** (`app/models/task_model.py`): Versión permisiva para endpoints de IA.
  - Acepta valores inválidos en `effort_hours` y los convierte a `null`.
  - `to_task()`: convierte a objeto `task` estricto.

- **task_create / task_schema** (`app/models/task_schema.py`): Esquemas para BD.
  - `task_create`: para crear tareas (sin id).
  - `task_schema`: para respuestas con id.

- **user_story_create / user_story_schema** (`app/models/user_story_schema.py`): Esquemas para historias.
  - `user_story_create`: para crear historias (sin id).
  - `user_story_schema`: para respuestas con id.

### Modelos ORM SQLAlchemy (app/database/)

- **user_story** (`app/database/models.py`): Modelo ORM para tabla `user_stories`.
  - Campos: id, project, role, goal, reason, description, priority, story_points, effort_hours, tasks_total_hours, created_at.
  - Relación: `tasks` (one-to-many con cascade delete).

- **task** (`app/database/models.py`): Modelo ORM para tabla `tasks`.
  - Campos: id, title, description, priority, effort_hours, status, assigned_to, category_id, risk_analysis, risk_mitigation, user_story_id, created_at.
  - Relación: `user_story` (many-to-one FK).

### Servicios (app/services/)

- **task_service** (`app/services/task_service.py`): CRUD de tareas en MySQL.
  - `create_task(db, task_data)`: crea tarea en BD.
  - `get_task(db, task_id)`: obtiene tarea por ID.
  - `get_all_tasks(db)`: lista todas las tareas.
  - `get_tasks_by_user_story(db, story_id)`: tareas de una historia.
  - `update_task(db, task_id, task_data)`: actualiza tarea.
  - `delete_task(db, task_id)`: elimina tarea.

- **user_story_service** (`app/services/user_story_service.py`): CRUD de historias en MySQL.
  - `create_user_story(db, story_data)`: crea historia en BD.
  - `get_user_story(db, story_id)`: obtiene historia por ID.
  - `get_all_user_stories(db)`: lista todas las historias.
  - `update_tasks_total_hours(db, story_id)`: actualiza horas totales.

- **ai_user_story_service** (`app/services/ai_user_story_service.py`): Generación con IA.
  - `generate_user_story(prompt, db)`: genera historia completa desde prompt.
  - `determine_category_from_description(story_dict, db)`: detecta categoría.
  - `generate_tasks_for_story(story_dict, category, num_tasks)`: genera tareas.

- **llm_service** (`app/services/llm_service.py`): Cliente Azure OpenAI.
  - `generate_description(task)`: genera descripción con IA.
  - `categorize_task(task)`: categoriza tarea con IA.
  - `estimate_effort(task)`: estima horas con IA.
  - `audit_task(task)`: genera análisis de riesgos y mitigación.

- **task_manager** (`app/services/task_manager.py`): **(Legacy)** Manejo de JSON.
  - Mantenido para compatibilidad, pero ya no se usa activamente.

## configuracion_llm

La configuración del LLM se encuentra en `app/core/llm_settings.json`. Debes configurar tus credenciales de Azure OpenAI:

```json
{
  "azure_openai": {
    "endpoint": "https://YOUR_AZURE_ENDPOINT.openai.azure.com/",
    "api_key": "YOUR_API_KEY"
  },
  "model_parameters": {
    "modelo": "YOUR_MODEL_DEPLOYMENT_NAME",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

### campos_de_configuracion

| Campo | Descripción |
|-------|-------------|
| `endpoint` | URL de tu recurso Azure OpenAI (ej: `https://tu-recurso.openai.azure.com/`) |
| `api_key` | Clave de API de Azure OpenAI |
| `modelo` | Nombre del deployment de tu modelo en Azure (ej: `gpt-4o`, `gpt-35-turbo`) |
| `temperature` | Control de creatividad (0.0-1.0). Menor = más determinista |
| `max_tokens` | Máximo de tokens en la respuesta |
| `top_p` | Muestreo de núcleo (0.0-1.0) |
| `frequency_penalty` | Penalización por repetición de tokens (0.0-2.0) |
| `presence_penalty` | Penalización por presencia de tokens (0.0-2.0) |

---

## 🔧 archivos_de_configuración_requeridos

> **⚠️ IMPORTANTE**: Antes de ejecutar la aplicación, **DEBES configurar estos 2 archivos**:

### 1️⃣ settingsApp.json (Configuración de Base de Datos)

**Ubicación**: Raíz del proyecto  
**Propósito**: Conexión a MySQL

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "TU_PASSWORD_MYSQL_AQUI",
    "database": "task_management_db",
    "echo": false,
    "pool_size": 5,
    "max_overflow": 10
  },
  "app": {
    "name": "gestor_de_tareas_fastapi",
    "version": "2.0.0",
    "description": "api_rest_para_la_gestion_de_tareas_y_historias_de_usuario_con_base_de_datos_mysql"
  }
}
```

**Campos críticos a modificar**:
- ✏️ `user`: Tu usuario de MySQL (típicamente `root`)
- ✏️ `password`: **Tu contraseña de MySQL** (campo obligatorio)
- ✏️ `database`: Nombre de la BD (usar `task_management_db`)

### 2️⃣ app/core/llm_settings.json (Configuración Azure OpenAI)

**Ubicación**: `app/core/llm_settings.json`  
**Propósito**: Credenciales de Azure OpenAI para generación con IA

```json
{
  "azure_openai": {
    "endpoint": "https://TU-RECURSO.openai.azure.com/",
    "api_key": "TU_API_KEY_DE_AZURE_OPENAI"
  },
  "model_parameters": {
    "modelo": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

**Campos críticos a modificar**:
- ✏️ `endpoint`: URL de tu recurso Azure OpenAI
- ✏️ `api_key`: **API Key de Azure** (campo obligatorio)
- ✏️ `modelo`: Nombre del deployment (ej: `gpt-4`, `gpt-35-turbo`)

### ✅ Verificar configuración

Después de editar los archivos, verifica:

```bash
# Verificar que settingsApp.json existe y tiene formato válido
python -c "import json; print(json.load(open('settingsApp.json'))['database']['host'])"

# Verificar que llm_settings.json existe
python -c "import json; print(json.load(open('app/core/llm_settings.json'))['azure_openai']['endpoint'])"
```

---

## instalación_y_ejecución

> **⚠️ IMPORTANTE**: Este proyecto requiere **MySQL** y **Azure OpenAI** configurados correctamente.

### 1. requisitos_previos

- **Python 3.12+** instalado
- **MySQL 5.7+** instalado y corriendo
- **Cuenta Azure OpenAI** con API key válida

### 2. configurar_base_de_datos_mysql

**Paso 2.1**: Configurar conexión en `settingsApp.json` (en la raíz del proyecto):

> **💡 Nota**: Ya NO necesitas crear manualmente la base de datos. El script `init_db.py` lo hace automáticamente.

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "TU_PASSWORD_AQUI",
    "database": "task_management_db",
    "echo": false,
    "pool_size": 5,
    "max_overflow": 10
  },
  "app": {
    "name": "gestor_de_tareas_fastapi",
    "version": "2.0.0",
    "description": "api_rest_para_la_gestion_de_tareas_y_historias_de_usuario_con_base_de_datos_mysql"
  }
}
```

**Campos a configurar**:
- `user`: Tu usuario de MySQL (por defecto: `root`)
- `password`: Tu contraseña de MySQL
- `database`: Nombre de la BD creada (`task_management_db`)
- `host`: Servidor MySQL (por defecto: `localhost`)
- `port`: Puerto MySQL (por defecto: `3306`)

### 3. crear_entorno_virtual

Desde la raíz del proyecto:

```bash
python -m venv venv
```

Activar el entorno (Windows PowerShell):

```bash
.\venv\Scripts\Activate.ps1
```

### 4. instalar_dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales**:
- `fastapi` - Framework web
- `sqlalchemy` - ORM para MySQL
- `pymysql` - Driver MySQL
- `jinja2` - Templates HTML
- `openai` - Cliente Azure OpenAI
- `pydantic` - Validación de datos

### 5. inicializar_base_de_datos_y_tablas

```bash
python init_db.py
```

**Este script automáticamente**:
1. ✅ Verifica si la base de datos `task_management_db` existe
2. ✅ **Crea la base de datos** si no existe (con charset utf8mb4)
3. ✅ Crea las tablas: `user_stories` y `tasks` con relaciones FK

**Salida esperada**:
```
🔧 Inicializando base de datos...

🔍 Verificando base de datos 'task_management_db'...
📦 Creando base de datos 'task_management_db'...
✅ Base de datos 'task_management_db' creada exitosamente!

📋 Creando tablas...
✅ Tablas creadas exitosamente!

📊 Tablas disponibles:
   • user_stories
   • tasks

🎉 Inicialización completada!
```

> **💡 Nota**: Ya NO necesitas crear manualmente la base de datos en MySQL. El script lo hace automáticamente.

### 6. configurar_azure_openai

Edita el archivo `app/core/llm_settings.json` con tus credenciales:

```json
{
  "azure_endpoint": "https://TU_RECURSO.openai.azure.com/",
  "api_key": "TU_API_KEY_AQUI",
  "api_version": "2024-02-15-preview",
  "deployment_name": "gpt-4",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### 7. ejecutar_la_aplicación

```bash
uvicorn app.main:app --reload
```

**URLs disponibles**:
- 🌐 **Interfaz Web** (Historias de Usuario): `http://localhost:8000/user-stories`
- 📖 **API Swagger** (Documentación interactiva): `http://localhost:8000/docs`
- 📚 **API ReDoc** (Documentación alternativa): `http://localhost:8000/redoc`

### 8. verificar_instalación

Abre el navegador en `http://localhost:8000/user-stories`. Deberías ver:
- Página con diseño Bootstrap (tonos grises)
- Formulario para generar historias con IA
- Lista de historias (vacía inicialmente)

## endpoints_disponibles

### endpoints_crud_tareas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/tasks` | Crear una nueva tarea |
| GET | `/tasks` | Obtener todas las tareas |
| GET | `/tasks/{task_id}` | Obtener una tarea por ID |
| PUT | `/tasks/{task_id}` | Actualizar una tarea |
| DELETE | `/tasks/{task_id}` | Eliminar una tarea |

### endpoints_ia

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/ai/tasks/describe` | Generar descripción con IA |
| POST | `/ai/tasks/categorize` | Categorizar tarea con IA |
| POST | `/ai/tasks/estimate` | Estimar esfuerzo con IA |
| POST | `/ai/tasks/audit` | Auditar riesgos con IA |

> **Nota sobre validación en endpoints de IA:** Los endpoints `/ai/tasks/*` tienen validación permisiva. Valores inválidos en campos como `effort_hours` (0, negativos, vacíos, texto) se convierten automáticamente a `null` para que la IA pueda procesarlos. Esto permite enviar tareas incompletas o con datos parciales para que la IA complete la información faltante.

### endpoints_mvc_historias_de_usuario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/user-stories` | Página HTML con todas las historias |
| POST | `/user-stories` | Crear historia desde prompt con IA |
| POST | `/user-stories/{id}/generate-tasks` | Generar tareas para una historia |
| GET | `/user-stories/{id}/tasks` | Página HTML con tareas de una historia |

---

## diagramas_de_flujo_endpoints_mvc

### 1. GET /user-stories - Listar Historias de Usuario

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuario abre: http://localhost:8000/user-stories               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_stories_router.py                                         │
│  @router.get("")                                                │
│  async def get_user_stories_page()                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_story_service.get_all_user_stories(db)                    │
│  → SELECT * FROM user_stories                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  templates.TemplateResponse("user_stories.html")                │
│  → Renderiza HTML con Jinja2 + Bootstrap                        │
│  → Muestra formulario + lista de historias                      │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2. POST /user-stories - Crear Historia con IA

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuario escribe prompt en textarea                              │
│  Ej: "Sistema de login con OAuth2 y JWT"                        │
│  Click: "✨ Generar Historia con IA"                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  POST /user-stories                                              │
│  Form Data: prompt="Sistema de login con OAuth2..."             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_stories_router.py                                         │
│  @router.post("")                                               │
│  async def create_user_story_from_prompt(prompt: str)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ai_user_story_service.generate_user_story(prompt, db)          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ 1. Construye prompt para Azure OpenAI                       ││
│  │ 2. llm_service.client.chat.completions.create()            ││
│  │ 3. Parsea JSON con campos:                                  ││
│  │    - project, role, goal, reason                            ││
│  │    - description, priority, story_points, effort_hours      ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_story_service.create_user_story(db, user_story_data)      │
│  → INSERT INTO user_stories (...)                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  RedirectResponse(url="/user-stories", status_code=303)         │
│  → Redirige a la página de historias                            │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3. POST /user-stories/{id}/generate-tasks - Generar Tareas con IA

Este es el endpoint más complejo. Utiliza internamente los servicios de IA.

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuario hace click en "🎯 Generar Tareas"                      │
│  en una historia de usuario existente                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  POST /user-stories/{id}/generate-tasks                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_stories_router.py                                         │
│  @router.post("/{user_story_id}/generate-tasks")                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Obtener historia de BD                                      │
│     user_story_service.get_user_story(db, user_story_id)        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Determinar categoría principal                              │
│     ai_user_story_service.determine_category_from_description() │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ Analiza description con LLM:                            │ │
│     │ "OAuth2, JWT, autenticación" → "Backend"                │ │
│     └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Generar tareas de esa categoría                             │
│     ai_user_story_service.generate_tasks_for_story(             │
│         story_dict, category="Backend", num_tasks=4             │
│     )                                                           │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ LLM genera 4 tareas con:                                │ │
│     │ - title, description, priority, status, assigned_to     │ │
│     └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Para CADA tarea, mejorar con servicios de IA:               │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │ a) llm_service.generate_description(task)               │ │
│     │    → Similar a POST /ai/tasks/describe                  │ │
│     │                                                         │ │
│     │ b) llm_service.estimate_effort(task)                    │ │
│     │    → Similar a POST /ai/tasks/estimate                  │ │
│     │                                                         │ │
│     │ c) llm_service.audit_task(task)                         │ │
│     │    → Similar a POST /ai/tasks/audit                     │ │
│     │    → Genera risk_analysis y risk_mitigation             │ │
│     └─────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Guardar cada tarea en BD                                    │
│     task_service.create_task(db, task_create)                   │
│     → INSERT INTO tasks (...)                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Actualizar total de horas en historia                       │
│     user_story_service.update_tasks_total_hours(db, story_id)   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  RedirectResponse(url="/user-stories/{id}/tasks", 303)          │
│  → Redirige a la página de tareas                               │
└─────────────────────────────────────────────────────────────────┘
```

#### Reutilización de Endpoints de IA en Generación de Tareas

| Servicio IA | Endpoint Original | Usado en Generación |
|-------------|-------------------|---------------------|
| `llm_service.generate_description()` | `POST /ai/tasks/describe` | ✅ Sí |
| `llm_service.estimate_effort()` | `POST /ai/tasks/estimate` | ✅ Sí |
| `llm_service.audit_task()` | `POST /ai/tasks/audit` | ✅ Sí |
| `determine_category_from_description()` | Similar a `/ai/tasks/categorize` | ✅ Adaptado |

---

### 4. GET /user-stories/{id}/tasks - Ver Tareas de una Historia

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuario accede a: /user-stories/5/tasks                        │
│  (después de generar tareas o via link "👁 Ver Tareas")        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  user_stories_router.py                                         │
│  @router.get("/{user_story_id}/tasks")                          │
│  async def get_user_story_tasks_page()                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. user_story_service.get_user_story(db, user_story_id)        │
│     → SELECT * FROM user_stories WHERE id = 5                   │
│                                                                 │
│  2. task_service.get_tasks_by_user_story(db, user_story_id)     │
│     → SELECT * FROM tasks WHERE user_story_id = 5               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  templates.TemplateResponse("tasks.html")                       │
│  → Renderiza HTML con Jinja2 + Bootstrap                        │
│  → Muestra: cabecera historia + lista tareas (acordeón)        │
│  → Cada tarea muestra: risk_analysis, risk_mitigation          │
└─────────────────────────────────────────────────────────────────┘
```

---

## flujo_completo_de_la_aplicación

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           FLUJO COMPLETO                                     │
└──────────────────────────────────────────────────────────────────────────────┘

Usuario abre http://localhost:8000/user-stories
                    │
                    ▼
            ┌───────────────┐
            │ GET           │
            │ /user-stories │
            └───────┬───────┘
                    │
                    ▼
         ┌──────────────────────┐
         │  user_stories.html   │
         │  ┌────────────────┐  │
         │  │  Formulario    │  │
         │  │  + Prompt IA   │  │
         │  └────────┬───────┘  │
         │           │          │
         │  ┌────────▼───────┐  │
         │  │ Lista Historias│  │
         │  │ [Generar]      │  │
         │  │ [Ver Tareas]   │  │
         │  └────────────────┘  │
         └──────────────────────┘
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
┌──────────┐  ┌───────────┐  ┌─────────────┐
│ POST     │  │ POST      │  │ GET         │
│ /user-   │  │ /{id}/    │  │ /{id}/tasks │
│ stories  │  │ generate- │  │             │
│          │  │ tasks     │  │             │
└────┬─────┘  └─────┬─────┘  └──────┬──────┘
     │              │               │
     ▼              ▼               ▼
┌──────────┐  ┌───────────┐  ┌─────────────┐
│ AI:      │  │ AI:       │  │ BD Query:   │
│ generate │  │ determine │  │ SELECT *    │
│ _user_   │  │ _category │  │ FROM tasks  │
│ story()  │  │ generate_ │  │ WHERE       │
│          │  │ tasks()   │  │ story_id=X  │
└────┬─────┘  └─────┬─────┘  └──────┬──────┘
     │              │               │
     ▼              ▼               ▼
┌──────────┐  ┌───────────┐  ┌─────────────┐
│ INSERT   │  │ Para cada │  │ tasks.html  │
│ INTO     │  │ tarea:    │  │ ┌─────────┐ │
│ user_    │  │ -describe │  │ │Historia │ │
│ stories  │  │ -estimate │  │ │ + Info  │ │
│          │  │ -audit    │  │ ├─────────┤ │
└────┬─────┘  │ INSERT    │  │ │ Tareas  │ │
     │        │ INTO tasks│  │ │(acordeón)│ │
     │        └─────┬─────┘  │ │-análisis│ │
     │              │        │ │-riesgos │ │
     │              │        │ └─────────┘ │
     │              │        └─────────────┘
     │              │               │
     ▼              ▼               │
┌─────────────────────────────┐    │
│  Redirect 303 →             │◄───┘
│  /user-stories              │
│  o /user-stories/{id}/tasks │
└─────────────────────────────┘
```

---

## ejemplos_de_uso

### crear_tarea_completa

```bash
curl -X POST "http://127.0.0.1:8000/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "implementar_autenticacion_jwt",
    "description": "Implementar sistema de autenticación usando JWT",
    "priority": "alta",
    "effort_hours": 16.0,
    "status": "pendiente",
    "assigned_to": "desarrollador_backend",
    "category": "Backend",
    "risk_analysis": null,
    "risk_mitigation": null
  }'
```

### generar_descripcion_con_ia

```bash
curl -X POST "http://127.0.0.1:8000/ai/tasks/describe" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "optimizar_consultas_base_datos",
    "description": "",
    "priority": "media",
    "status": "pendiente",
    "assigned_to": "dba"
  }'
```

**Respuesta:**
```json
{
  "id": null,
  "title": "optimizar_consultas_base_datos",
  "description": "Esta tarea consiste en revisar y optimizar las consultas SQL existentes en la base de datos para mejorar el rendimiento general del sistema...",
  "priority": "media",
  "effort_hours": null,
  "status": "pendiente",
  "assigned_to": "dba",
  "category": null,
  "risk_analysis": null,
  "risk_mitigation": null
}
```

### categorizar_tarea_con_ia

```bash
curl -X POST "http://127.0.0.1:8000/ai/tasks/categorize" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "crear_tests_unitarios_api",
    "description": "Crear tests unitarios para validar todos los endpoints de la API",
    "priority": "media",
    "status": "pendiente",
    "assigned_to": "qa_engineer"
  }'
```

**Respuesta:**
```json
{
  "id": null,
  "title": "crear_tests_unitarios_api",
  "description": "Crear tests unitarios para validar todos los endpoints de la API",
  "priority": "media",
  "effort_hours": null,
  "status": "pendiente",
  "assigned_to": "qa_engineer",
  "category": "Testing",
  "risk_analysis": null,
  "risk_mitigation": null
}
```

### estimar_esfuerzo_con_ia

```bash
curl -X POST "http://127.0.0.1:8000/ai/tasks/estimate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "migrar_base_datos_mongodb",
    "description": "Migrar todos los datos de PostgreSQL a MongoDB incluyendo scripts de transformación",
    "priority": "alta",
    "status": "pendiente",
    "assigned_to": "dba",
    "category": "Database"
  }'
```

**Respuesta:**
```json
{
  "id": null,
  "title": "migrar_base_datos_mongodb",
  "description": "Migrar todos los datos de PostgreSQL a MongoDB incluyendo scripts de transformación",
  "priority": "alta",
  "effort_hours": 32.0,
  "status": "pendiente",
  "assigned_to": "dba",
  "category": "Database",
  "risk_analysis": null,
  "risk_mitigation": null
}
```

### auditar_riesgos_con_ia

```bash
curl -X POST "http://127.0.0.1:8000/ai/tasks/audit" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "desplegar_produccion_microservicios",
    "description": "Desplegar la nueva versión de microservicios en el cluster de producción",
    "priority": "bloqueante",
    "effort_hours": 8.0,
    "status": "pendiente",
    "assigned_to": "devops_engineer",
    "category": "DevOps"
  }'
```

**Respuesta:**
```json
{
  "id": null,
  "title": "desplegar_produccion_microservicios",
  "description": "Desplegar la nueva versión de microservicios en el cluster de producción",
  "priority": "bloqueante",
  "effort_hours": 8.0,
  "status": "pendiente",
  "assigned_to": "devops_engineer",
  "category": "DevOps",
  "risk_analysis": "Riesgos identificados: 1. Tiempo de inactividad durante el despliegue que puede afectar a usuarios finales. 2. Incompatibilidad con versiones anteriores de la API...",
  "risk_mitigation": "Plan de mitigación: 1. Implementar estrategia blue-green deployment para minimizar tiempo de inactividad. 2. Realizar pruebas exhaustivas en ambiente de staging..."
}
```

## categorias_disponibles

Las categorías disponibles para las tareas son:

- `Frontend` - Desarrollo de interfaces de usuario
- `Backend` - Desarrollo de lógica de servidor
- `Testing` - Pruebas y QA
- `Infra` - Infraestructura
- `DevOps` - Operaciones y despliegue
- `Database` - Bases de datos
- `Security` - Seguridad
- `API` - Desarrollo de APIs
- `UI_UX` - Diseño de experiencia de usuario
- `Documentation` - Documentación
- `Architecture` - Arquitectura de software
- `Mobile` - Desarrollo móvil
- `Cloud` - Servicios en la nube
- `Analytics` - Análisis y métricas

## ejecutar_tests

```bash
pytest -v
```

Para ejecutar solo los tests de endpoints de IA:

```bash
pytest tests/test_ai_endpoints.py -v
```

## ejemplo_de_uso

## errores_comunes (índice_rápido)

- [errores_de_validación_422](#errores_de_validación_422)
- [valores_permitidos_y_validación](#valores_permitidos_y_validación)
- [errores_específicos_effort_hours](#errores_específicos_effort_hours)
- [errores_formato_campos_string](#errores_formato_campos_string)
- [errores_campos_vacíos](#errores_campos_vacíos)

### crear_una_tarea (POST `/tasks`)

```json
{
  "title": "tarea_de_ejemplo",
  "description": "descripcion_de_la_tarea",
  "priority": "alta",
  "effort_hours": 4.5,
  "status": "pendiente",
  "assigned_to": "juan_perez"
}
```

#### errores_de_validación_422

Errores de validación (422 Unprocessable Content):

- Si faltan campos requeridos en el cuerpo, la API devuelve un objeto con `msg` indicando cuáles faltan.
- Ejemplo de respuesta cuando faltan campos:

```json
{
  "msg": "Faltan los siguientes campos requeridos: description, priority, effort_hours, status, assigned_to"
}
```

Notas:
- El campo `id` no debe enviarse; se asigna automáticamente.
- Los valores de `priority` y `status` deben corresponder a los permitidos por el esquema.

#### valores_permitidos_y_validación

Valores permitidos y validación:

- `priority`: baja, media, alta, bloqueante
- `status`: pendiente, en_progreso, en_revision, completada

Si se envía un valor inválido, la API responde 422 (Unprocessable Content) con errores de validación estándar en `detail`.

Ejemplo de solicitud inválida (priority no permitido):

```json
{
  "title": "tarea_invalida",
  "description": "desc",
  "priority": "urgente",
  "effort_hours": 1.0,
  "status": "pendiente",
  "assigned_to": "alguien"
}
```

Ejemplo de respuesta (resumen):

```json
{
  "detail": [
    {
      "loc": ["body", "priority"],
      "msg": "Input should be 'baja' or 'media' or 'alta' or 'bloqueante'",
      "type": "literal_error"
    }
  ]
}
```

#### errores_específicos_effort_hours

Errores específicos para `effort_hours`:

- No numérico:

  Solicitud (ejemplo):

  ```json
  {
    "title": "tarea",
    "description": "desc",
    "priority": "alta",
    "effort_hours": "hola",
    "status": "pendiente",
    "assigned_to": "usuario"
  }
  ```

  Respuesta:

  ```json
  {
    "msg": "effort_hours debe ser numérico",
    "detail": [
      {
        "type": "float_type",
        "loc": ["body", "effort_hours"],
        "msg": "Input should be a valid number",
        "input": "hola"
      }
    ]
  }
  ```

- Menor o igual a cero:

  Solicitud (ejemplo):

  ```json
  {
    "title": "tarea",
    "description": "desc",
    "priority": "alta",
    "effort_hours": 0,
    "status": "pendiente",
    "assigned_to": "usuario"
  }
  ```

  Respuesta:

  ```json
  {
    "msg": "effort_hours debe ser mayor a 0",
    "detail": [
      {
        "type": "greater_than",
        "loc": ["body", "effort_hours"],
        "msg": "Input should be greater than 0",
        "input": 0
      }
    ]
  }
  ```

- JSON inválido (token sin comillas):

  Solicitud (ejemplo):

  ```json
  {"title":"x","description":"y","priority":"alta","effort_hours": ew, "status":"pendiente","assigned_to":"z"}
  ```

  Respuesta:

  ```json
  {
    "msg": "effort_hours debe ser numérico",
    "detail": [
      {
        "type": "json_invalid",
        "loc": ["body", 95],
        "msg": "JSON decode error",
        "ctx": {"error": "Expecting value"}
      }
    ]
  }
  ```

  #### errores_formato_campos_string

  Errores de formato en campos string (JSON inválido, valores sin comillas):

  - Si un campo de texto del esquema (`title`, `description`, `priority`, `status`, `assigned_to`) se envía sin comillas dobles en un JSON inválido, la API devuelve un 422 con un mensaje claro indicando el formato incorrecto.

  Ejemplos:

  - Priority sin comillas:

    Solicitud:

    ```json
    {"title":"x","description":"y","priority": urgente, "effort_hours": 1.0, "status":"pendiente","assigned_to":"z"}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "priority tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```

  - Title sin comillas:

    Solicitud:

    ```json
    {"title": x, "description":"y","priority":"alta", "effort_hours": 1.0, "status":"pendiente","assigned_to":"z"}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "title tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```

  - Status sin comillas:

    Solicitud:

    ```json
    {"title":"x","description":"y","priority":"alta", "effort_hours": 1.0, "status": pendiente, "assigned_to":"z"}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "status tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```

  Caso combinado (sin confusión con effort_hours):

  - Priority sin comillas y effort_hours válido:

    Solicitud:

    ```json
    {"title":"x","description":"y","priority": alta, "effort_hours": 4.5, "status":"pendiente","assigned_to":"z"}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "priority tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```
    Nota: No agrega "effort_hours debe ser numérico" porque `effort_hours` es un número válido (4.5).

  - Description sin comillas:

    Solicitud:

    ```json
    {"title":"x","description": descripcion_larga, "priority":"alta", "effort_hours": 1.0, "status":"pendiente","assigned_to":"z"}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "description tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```

  - Assigned_to sin comillas:

    Solicitud:

    ```json
    {"title":"x","description":"y","priority":"alta", "effort_hours": 1.0, "status":"pendiente","assigned_to": usuario_sin_comillas}
    ```

    Respuesta (resumen):

    ```json
    {
      "msg": "assigned_to tiene formato inválido: debe ser texto entre comillas dobles",
      "detail": [
        { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
      ]
    }
    ```

Nota de datos legados:
- Si existen tareas inválidas en `data/tasks_json.json` (por ejemplo, `effort_hours`=0), el sistema las omite al cargar para evitar errores.

#### errores_campos_vacíos

Errores de campos con valor vacío (JSON inválido con sintaxis `"campo": ,`):

- Si un campo se envía con valor vacío en formato JSON inválido, la API identifica específicamente el campo problemático.

Ejemplo - Category vacío:

Solicitud:

```json
{"title":"tarea","description":"desc","priority":"alta","effort_hours":4.5,"status":"pendiente","assigned_to":"usuario","category": ,"risk_analysis":null,"risk_mitigation":null}
```

Respuesta:

```json
{
  "msg": "category tiene valor vacío o formato inválido",
  "detail": [
    { "type": "json_invalid", "loc": ["body", ...], "msg": "JSON decode error" }
  ]
}
```

Nota: Este tipo de error aplica a cualquier campo que tenga la sintaxis `"campo": ,` o `"campo": }` en el JSON.

### leer_todas_las_tareas (GET `/tasks`)

Devuelve una lista con todas las tareas almacenadas.

### leer_una_tarea (GET `/tasks/{id}`)

Devuelve la tarea con el `id` indicado si existe.

### actualizar_una_tarea (PUT `/tasks/{id}`)

Recibe un cuerpo JSON con el mismo esquema que la creación y reemplaza los datos de la tarea indicada.

### eliminar_una_tarea (DELETE `/tasks/{id}`)

Elimina la tarea con el `id` indicado y devuelve una confirmación.

## pruebas_con_pytest

Para ejecutar las pruebas automatizadas:

```bash
pytest
```

Los tests incluyen la validación del mensaje de error en la creación de tareas cuando faltan campos requeridos.

---

# 🆕 NUEVAS FUNCIONALIDADES - VERSIÓN 2.0

## cambios_principales_v2.0

La **versión 2.0** introduce un cambio fundamental en la arquitectura del proyecto:

- ❌ **Eliminado**: Almacenamiento en archivos JSON (`data/tasks_json.json`)
- ✅ **Agregado**: **Base de datos MySQL** con SQLAlchemy ORM
- ✅ **Agregado**: **Historias de usuario** con generación automática por IA
- ✅ **Agregado**: **Interfaces web HTML** usando Jinja2 y Bootstrap
- ✅ **Agregado**: Generación automática de tareas para historias de usuario

### comparativa_versiones

| Aspecto | v1.0 (Legacy) | v2.0 (Actual) |
|---------|---------------|---------------|
| **Almacenamiento** | JSON (tasks_json.json) | MySQL con SQLAlchemy |
| **Historias de Usuario** | No existía | ✅ Completo con IA |
| **Interfaz** | Solo API REST JSON | ✅ MVC HTML + API REST |
| **Templates** | No existía | ✅ Jinja2 + Bootstrap 5.3 |
| **Generación IA** | Solo para tareas | ✅ Historias y tareas |
| **Services** | 2 servicios | ✅ 6 servicios especializados |
| **Modelos BD** | - | ✅ SQLAlchemy ORM (2 tablas) |
| **Schemas Pydantic** | 1 (task_model) | ✅ 10 schemas (5+5) |
| **Endpoints** | 5 CRUD + 4 IA | ✅ 5 CRUD + 4 IA + 4 MVC |
| **Tests** | 2 archivos | ✅ 4 archivos |
| **Git** | No inicializado | ✅ Repositorio inicializado |

## estructura_del_proyecto_actualizada

```text
project_root/
│── app/
│   ├── main.py
│   ├── database/                    # ✨ NUEVO
│   │   ├── database.py              # Configuración SQLAlchemy
│   │   └── models.py                # Modelos ORM (UserStory, Task)
│   ├── api/
│   │   ├── tasks_router.py
│   │   ├── ai_router.py
│   │   └── user_stories_router.py   # ✨ NUEVO - Endpoints MVC
│   ├── services/
│   │   ├── task_manager.py          # Mantiene compatibilidad legacy
│   │   ├── task_service.py          # ✨ NUEVO - CRUD con BD
│   │   ├── user_story_service.py    # ✨ NUEVO - CRUD historias
│   │   ├── ai_user_story_service.py # ✨ NUEVO - Generación IA
│   │   └── llm_service.py
│   ├── models/
│   │   ├── task_model.py            # Legacy Pydantic
│   │   ├── task_schema.py           # ✨ NUEVO - Schemas para BD
│   │   └── user_story_schema.py     # ✨ NUEVO - Schemas historias
│   └── core/
│       ├── config.py
│       └── llm_settings.json
│
│── templates/                       # ✨ NUEVO
│   ├── user_stories.html            # Interfaz de historias
│   └── tasks.html                   # Interfaz de tareas
│
│── tests/
│   ├── test_tasks_api.py
│   ├── test_ai_endpoints.py
│   ├── test_user_stories_endpoints.py   # ✨ NUEVO
│   └── test_database_services.py        # ✨ NUEVO
│
│── settingsApp.json                 # ✨ NUEVO - Config BD y app
│── init_db.py                       # ✨ NUEVO - Script inicialización
│── requirements.txt
│── .gitignore
│── README.md
```

## nuevas_clases_y_servicios

### Modelos SQLAlchemy (app/database/models.py)

- **Clase user_story**: Modelo ORM para historias de usuario
  - Campos: id, project, role, goal, reason, description, priority, story_points, effort_hours, created_at
  - Relación: one-to-many con Task (cascade delete)

- **Clase task**: Modelo ORM para tareas
  - Campos: todos los anteriores + user_story_id (FK)
  - Relación: many-to-one con UserStory

### Servicios de Base de Datos

- **Clase user_story_service** (app/services/user_story_service.py):
  - `create_user_story(db, user_story_data)`: crea historia en BD
  - `get_user_story(db, user_story_id)`: obtiene historia por ID
  - `get_all_user_stories(db, skip, limit)`: lista con paginación
  - `update_user_story(db, user_story_id, data)`: actualiza historia
  - `delete_user_story(db, user_story_id)`: elimina historia (y sus tareas)
  - `get_user_stories_by_project(db, project_name)`: filtra por proyecto

- **Clase task_service** (app/services/task_service.py):
  - `create_task(db, task_data)`: crea tarea en BD
  - `get_task(db, task_id)`: obtiene tarea por ID
  - `get_all_tasks(db, skip, limit)`: lista con paginación
  - `get_tasks_by_user_story(db, user_story_id)`: tareas de una historia
  - `update_task(db, task_id, data)`: actualiza tarea
  - `delete_task(db, task_id)`: elimina tarea
  - `get_tasks_by_status(db, status)`: filtra por estado
  - `get_tasks_by_assigned(db, assigned_to)`: filtra por asignado

- **Clase ai_user_story_service** (app/services/ai_user_story_service.py):
  - `generate_user_story(prompt)`: genera historia completa desde texto
  - `generate_tasks_for_story(user_story_data, num_tasks)`: genera tareas automáticamente

## configuracion_base_de_datos

### archivo settingsApp.json

Configuración centralizada de la base de datos y aplicación:

```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password_here",
    "database": "task_management_db",
    "echo": false,
    "pool_size": 5,
    "max_overflow": 10
  },
  "app": {
    "name": "gestor_de_tareas_fastapi",
    "version": "2.0.0",
    "description": "api_rest_para_la_gestion_de_tareas_y_historias_de_usuario_con_base_de_datos_mysql"
  }
}
```

### inicialización_de_base_de_datos

1. **Crear base de datos MySQL**:
```sql
CREATE DATABASE task_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Ejecutar script de inicialización**:
```bash
python init_db.py
```

Este script crea automáticamente las tablas `user_stories` y `tasks` con todas sus relaciones.

## nuevos_endpoints_historias_de_usuario

### endpoints_mvc_html

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/user-stories` | Página HTML con todas las historias + formulario de generación con IA |
| POST | `/user-stories` | Crear historia de usuario desde prompt usando IA |
| POST | `/user-stories/{id}/generate-tasks` | Generar 5 tareas automáticamente para una historia |
| GET | `/user-stories/{id}/tasks` | Página HTML con las tareas de una historia específica |

### ejemplo_flujo_completo

1. **Acceder a interfaz web**: `http://localhost:8000/user-stories`
2. **Generar historia con IA**: Escribir en el textarea (ej: "Sistema de autenticación con Google y Facebook")
3. **La IA genera automáticamente**:
   - project (nombre del proyecto)
   - role (tipo de usuario)
   - goal (qué quiere lograr)
   - reason (por qué es importante)
   - description (descripción completa)
   - priority (prioridad sugerida)
   - story_points (estimación 1-8)
   - effort_hours (horas estimadas)
4. **Historia almacenada en MySQL**
5. **Generar tareas**: Click en botón "🎯 Generar Tareas"
6. **La IA genera 5 tareas técnicas** con título, descripción, categoría, esfuerzo, etc.
7. **Ver todas las tareas** en página dedicada

## interfaz_web_html

### diseño_y_estilo

Las interfaces web usan **Bootstrap 5.3** con un diseño en **tonos grises**:

- **Color primario**: #2c3e50 (gris oscuro)
- **Color secundario**: #34495e (gris medio)
- **Fondo**: #f8f9fa (gris claro)
- **Efectos**: Hover transforms, smooth transitions
- **Componentes**: Cards, badges, forms responsivos

### páginas_disponibles

1. **user_stories.html**:
   - Listado de historias en formato card
   - Formulario de generación con IA (textarea + botón)
   - Botones por historia: "Generar Tareas" y "Ver Tareas"
   - Badges de prioridad coloreados
   - Responsive mobile-first

2. **tasks.html**:
   - Información detallada de la historia de usuario
   - Grid de tareas en cards
   - Badges de estado y prioridad
   - Análisis de riesgos expandible (details/summary)
   - Botón para generar más tareas
   - Navegación de regreso

## esquemas_pydantic_actualizados

### user_story_schemas (app/models/user_story_schema.py)

- `user_story_base`: Esquema base con validaciones
- `user_story_create`: Para crear nuevas historias
- `user_story_update`: Para actualizaciones parciales
- `user_story_schema`: Respuesta completa (incluye ID y timestamps)
- `user_story_schemas`: Lista de historias
- `user_story_prompt`: Para recibir prompt de generación IA

### task_schemas (app/models/task_schema.py)

- `task_base`: Esquema base con validaciones
- `task_create`: Para crear nuevas tareas (incluye user_story_id)
- `task_update`: Para actualizaciones parciales
- `task_schema`: Respuesta completa (incluye ID y timestamps)
- `task_schemas`: Lista de tareas

## nuevos_tests

### test_user_stories_endpoints.py

Tests para endpoints MVC de historias:
- `test_get_user_stories_page()`: Verifica página HTML
- `test_get_user_stories_page_with_data()`: Con datos existentes
- `test_get_user_story_tasks_page()`: Página de tareas
- `test_create_user_story_from_prompt_mock()`: Generación con IA (mock)
- `test_generate_tasks_for_user_story_mock()`: Generación de tareas (mock)

### test_database_services.py

Tests para servicios CRUD con BD:
- Tests de `user_story_service` (create, get, update, delete)
- Tests de `task_service` (create, get, update, delete)
- Tests de relaciones (cascade delete)
- Tests de filtrado y búsqueda
- Usa SQLite en memoria para tests

### ejecutar_todos_los_tests

```bash
# Todos los tests
pytest

# Tests específicos de v2.0
pytest tests/test_user_stories_endpoints.py -v
pytest tests/test_database_services.py -v

# Con cobertura
pytest --cov=app --cov-report=html
```

## migración_de_datos_json_a_mysql

**Nota importante**: La carpeta `data/` y el archivo `tasks_json.json` han sido eliminados en v2.0.

Si tienes datos previos en JSON que deseas migrar:

1. Los endpoints CRUD de tareas (`/tasks`) ahora trabajan con MySQL
2. Puedes crear un script personalizado para leer tu JSON antiguo y usar endpoints POST para recrear las tareas
3. Las tareas legacy sin `user_story_id` se pueden crear con este campo en `null`

## compatibilidad_con_versión_anterior

### endpoints_crud_tareas_mantenidos

Los endpoints `/tasks` **siguen funcionando** pero ahora usan MySQL en lugar de JSON:

- `POST /tasks` - Crea tarea en BD
- `GET /tasks` - Lista desde BD
- `GET /tasks/{id}` - Obtiene desde BD
- `PUT /tasks/{id}` - Actualiza en BD
- `DELETE /tasks/{id}` - Elimina de BD

### endpoints_ia_mantenidos

Todos los endpoints de IA para tareas se mantienen sin cambios:

- `POST /ai/tasks/describe`
- `POST /ai/tasks/categorize`
- `POST /ai/tasks/estimate`
- `POST /ai/tasks/audit`

## arquitectura_v2.0

```
┌─────────────────────────────────────────┐
│      FastAPI Application (main.py)      │
│   HTTP Server + Middleware + Routers    │
└────────┬──────────────┬─────────────────┘
         │              │
    [MVC Layer]    [API Layer]
    HTML Views    JSON Responses
         │              │
         └──────┬───────┘
                │
       ┌────────▼────────┐
       │  Service Layer  │
       │  - user_story_  │
       │  - task_        │
       │  - ai_*         │
       └────────┬────────┘
                │
       ┌────────▼────────┐
       │ Database Layer  │
       │   SQLAlchemy    │
       │   MySQL/PyMySQL │
       └─────────────────┘
```

## relaciones_de_base_de_datos

```
user_stories (1) ──────< (N) tasks
    │                        │
    ├─ id (PK)              ├─ id (PK)
    ├─ project              ├─ title
    ├─ role                 ├─ description
    ├─ goal                 ├─ category
    ├─ reason               ├─ priority
    ├─ description          ├─ status
    ├─ priority             ├─ effort_hours
    ├─ story_points         ├─ user_story_id (FK)
    ├─ effort_hours         └─ created_at
    └─ created_at

Relación: CASCADE DELETE
(si se elimina una historia, se eliminan sus tareas)
```

## changelog_v2.0

### agregado
- ✅ Base de datos MySQL con SQLAlchemy ORM
- ✅ Modelos ORM: UserStory y Task
- ✅ Servicios CRUD para historias y tareas
- ✅ Endpoints MVC con HTML para historias
- ✅ Templates Jinja2 con Bootstrap 5.3
- ✅ Generación IA de historias completas desde prompt
- ✅ Generación IA de tareas para historias
- ✅ Archivo settingsApp.json para configuración
- ✅ Script init_db.py para inicialización
- ✅ Tests para nuevos endpoints y servicios
- ✅ Esquemas Pydantic para BD
- ✅ Relaciones FK entre tablas
- ✅ Interfaz web profesional

### modificado
- 📝 requirements.txt (añade sqlalchemy, pymysql, jinja2, python-multipart)
- 📝 app/main.py (incluye nuevo router MVC)
- 📝 app/core/config.py (lee desde settingsApp.json)

### eliminado
- ❌ Carpeta data/
- ❌ Archivo tasks_json.json
- ❌ Almacenamiento en archivos JSON

### mantenido
- ✅ Endpoints CRUD de tareas (ahora con BD)
- ✅ Endpoints de IA para tareas
- ✅ Validación y manejo de errores
- ✅ Configuración LLM
- ✅ Tests anteriores

## estadísticas_del_proyecto

| Métrica | Valor |
|---------|-------|
| **Versión** | 2.0.0 |
| **Líneas de código** | ~3,500+ |
| **Archivos creados** | 14 nuevos |
| **Archivos modificados** | 3 |
| **Endpoints nuevos** | 4 (MVC) |
| **Servicios nuevos** | 3 |
| **Esquemas Pydantic** | 10 (5+5) |
| **Modelos ORM** | 2 (UserStory, Task) |
| **Templates HTML** | 2 |
| **Tests nuevos** | 2 archivos |
| **Commits Git** | 3 |
| **Base de datos** | MySQL + SQLAlchemy |
| **Framework UI** | Bootstrap 5.3 |
| **Integración IA** | Azure OpenAI |

## conceptos_implementados

Este proyecto implementa los siguientes patrones y tecnologías avanzadas:

✅ **Arquitectura MVC** - Separación clara entre Modelo, Vista y Controlador  
✅ **Patrón Repository** - Servicios especializados por entidad  
✅ **ORM (SQLAlchemy)** - Mapeo objeto-relacional con MySQL  
✅ **Inyección de Dependencias** - FastAPI Depends() para gestión de sesiones  
✅ **Validación Pydantic** - Esquemas con validación automática  
✅ **Templates Jinja2** - Renderizado server-side de HTML  
✅ **Bootstrap 5** - Framework CSS responsivo y moderno  
✅ **API REST** - Endpoints RESTful con documentación automática  
✅ **Testing Unitario** - Pytest con bases de datos en memoria y mocks  
✅ **Generación con IA** - Prompts estructurados con Azure OpenAI  
✅ **Control de Versiones** - Git con .gitignore completo  
✅ **Configuración Centralizada** - Archivos JSON para settings  
✅ **Relaciones FK** - Integridad referencial con cascade delete  
✅ **Migraciones** - Script de inicialización de base de datos

## preguntas_frecuentes_v2.0

### ¿Qué pasó con mis datos en tasks_json.json?

El archivo fue eliminado. Ahora toda la información se almacena en MySQL. Si necesitas migrar datos antiguos, puedes hacerlo manualmente usando los endpoints POST.

### ¿Dónde configuro la conexión a MySQL?

En el archivo **`settingsApp.json`** ubicado en la raíz del proyecto. Debes editar:
- `user`: tu usuario de MySQL
- `password`: tu contraseña de MySQL
- `database`: nombre de la base de datos (`task_management_db`)

### ¿Cómo sé si la conexión a MySQL funciona?

Ejecuta `python init_db.py`. Si ves el mensaje de éxito, la conexión es correcta. Si hay error, verifica:
1. MySQL está corriendo
2. Las credenciales en `settingsApp.json` son correctas
3. La base de datos existe (`CREATE DATABASE task_management_db;`)

### ¿Qué error significa "Can't connect to MySQL server"?

Posibles causas:
- MySQL no está corriendo → Inicia el servicio MySQL
- Host/puerto incorrectos en `settingsApp.json` → Verifica `localhost:3306`
- Firewall bloqueando conexión → Permite puerto 3306

### ¿Qué error significa "Access denied for user"?

El usuario o contraseña en `settingsApp.json` son incorrectos. Verifica:
```bash
# Probar conexión desde terminal
mysql -u root -p
```

### ¿Qué error significa "Unknown database"?

Este error **ya no debería ocurrir** porque `init_db.py` ahora crea la base de datos automáticamente. Si lo ves, verifica:
- MySQL está corriendo
- Las credenciales en `settingsApp.json` son correctas
- El usuario tiene permisos para crear bases de datos

Si persiste, créala manualmente:
```sql
CREATE DATABASE task_management_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### ¿Dónde configuro Azure OpenAI?

En el archivo **`app/core/llm_settings.json`**. Necesitas:
- `azure_endpoint`: URL de tu recurso Azure OpenAI
- `api_key`: Tu API key
- `deployment_name`: Nombre del modelo desplegado (ej: `gpt-4`)

### ¿Necesito configurar algo adicional?

Sí, dos archivos de configuración son **obligatorios**:

1. **`settingsApp.json`** (raíz del proyecto):
   ```json
   {
     "database": {
       "host": "localhost",
       "user": "root",
       "password": "tu_password",
       "database": "task_management_db"
     }
   }
   ```

2. **`app/core/llm_settings.json`**:
   ```json
   {
     "azure_endpoint": "https://tu-recurso.openai.azure.com/",
     "api_key": "tu-api-key"
   }
   ```

### ¿Los endpoints anteriores siguen funcionando?

Sí, todos los endpoints de `/tasks` y `/ai/tasks/*` siguen funcionando exactamente igual, pero ahora usan MySQL en lugar de JSON.

### ¿Puedo usar SQLite en lugar de MySQL?

El código está configurado para MySQL, pero podrías adaptar `DATABASE_URL` en `app/database/database.py` para usar SQLite cambiando el driver.

### ¿Cómo genero una historia de usuario?

1. Abre `http://localhost:8000/user-stories`
2. Escribe una descripción en el textarea (ej: "Sistema de login con redes sociales")
3. Click en "Generar Historia con IA"
4. La IA creará automáticamente todos los campos

### ¿Cómo se relacionan las tareas con las historias?

Las tareas tienen un campo `user_story_id` (FK) que las vincula a una historia. Al eliminar una historia, sus tareas se eliminan automáticamente (CASCADE).

## checklist_de_requisitos_completados

Validación de todos los requisitos del Entregable 3:

- ✅ **Requisito 1**: Crear estructura de carpetas database/ con conexión MySQL
- ✅ **Requisito 2**: Conexión MySQL desde archivo settingsApp.json
- ✅ **Requisito 3**: Refinación y separación de servicios (6 servicios totales)
- ✅ **Requisito 4**: Esquemas Pydantic para BD (user_story_schema.py + task_schema.py)
- ✅ **Requisito 5**: Modelos SQLAlchemy (user_story + task con relaciones FK)
- ✅ **Requisito 6**: Endpoints MVC con HTML (4 endpoints nuevos)
- ✅ **Requisito 7**: Templates HTML con Jinja2 + Bootstrap (2 templates)
- ✅ **Requisito 8**: Servicio de IA para generación de historias (ai_user_story_service.py)
- ✅ **Requisito 9**: Actualización de main.py y requirements.txt
- ✅ **Requisito 10**: Script de inicialización BD (init_db.py)
- ✅ **Requisito Adicional**: Tests completos (test_user_stories_endpoints.py + test_database_services.py)
- ✅ **Requisito Adicional**: Repositorio Git inicializado con .gitignore
- ✅ **Requisito Adicional**: Eliminación de carpeta data/ y tasks_json.json
- ✅ **Requisito Adicional**: Documentación completa en README.md

**Estado**: 🎉 PROYECTO COMPLETADO AL 100%

## versión

**Versión actual**: 2.0.0  
**Fecha de actualización**: Febrero 2026  
**Compatibilidad**: Python 3.12+, MySQL 5.7+, FastAPI 0.100+  
**Entregable**: 3  
**Estado**: ✅ Producción
