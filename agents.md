# Cursor Agents Configuration

Este archivo define las reglas, responsabilidades y estándares que deben seguir
los agentes de Cursor para el desarrollo del proyecto.

---

## 🔹 Reglas globales del proyecto

- Todo el código debe seguir **snake_case** para:
  - nombres de clases
  - variables
  - métodos
  - archivos y carpetas
- El proyecto debe usar **Python 3.12**
- Se debe trabajar siempre dentro de un **entorno virtual**
- El proyecto debe usar **FastAPI** como framework principal
- La documentación de la API debe realizarse con **Swagger (OpenAPI)**
- Se debe usar **pytest** para pruebas automatizadas
- El proyecto debe tener **control de versiones con Git**
- La arquitectura debe ser **Modular**
- Los datos deben almacenarse en archivos **JSON** dentro de una carpeta `data/`

---

## 🤖 Agent: project_initializer

**Responsabilidad:**
Inicializar la estructura base del proyecto.

**Tareas:**
- Crear entorno virtual con Python 3.12
- Activar el entorno virtual
- Crear archivo `requirements.txt`
- Inicializar repositorio Git (`git init`)
- Crear `.gitignore` para Python
- Crear estructura base de carpetas

**Estructura esperada:**
Se debe manejar una estuctura modular:

project_root/
│── app/
│ ├── main.py
│ ├── api/
│ ├── services/
│ ├── models/
│ └── core/
│
│── data/
│ └── sample_data.json
│
│── tests/
│
│── requirements.txt
│── .gitignore
│── README.md


