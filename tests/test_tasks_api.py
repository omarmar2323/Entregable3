"""
Tests para los endpoints de tareas.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import fastapi_app
from app.database.database import Base, get_db


# Base de datos en memoria para tests con StaticPool para compartir conexión
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia get_db para tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Fixture que crea y destruye la base de datos para cada test."""
    # Override de la dependencia dentro del fixture
    fastapi_app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Fixture que proporciona el cliente de FastAPI."""
    return TestClient(fastapi_app)


def test_crear_tarea_faltan_campos(client):
    """
    Test para validar que si falta un campo requerido al crear una tarea,
    la respuesta incluye un msg con los campos faltantes.
    """
    tarea_incompleta = {
        "title": "tarea_incompleta",
        # Falta 'description', 'priority', 'effort_hours', 'status', 'assigned_to'
    }
    response = client.post("/tasks", json=tarea_incompleta)
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    # Debe mencionar los campos faltantes
    assert "description" in data["msg"]
    assert "priority" in data["msg"]
    assert "effort_hours" in data["msg"]
    assert "status" in data["msg"]
    assert "assigned_to" in data["msg"]


def test_crear_tarea(client):
    """
    Test para la creación de una nueva tarea vía POST /tasks.

    Valida que la respuesta sea 201, se le asigne id y que los campos coincidan.
    """
    nueva_tarea = {
        "title": "tarea_de_prueba",
        "description": "descripcion_de_prueba",
        "priority": "alta",
        "effort_hours": 2.5,
        "status": "pendiente",
        "assigned_to": "usuario_prueba",
    }
    response = client.post("/tasks", json=nueva_tarea)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == nueva_tarea["title"]


def test_crear_tarea_effort_hours_cero(client):
    """
    Validar que 'effort_hours' igual a 0 produce error 422 con detalle del campo.
    """
    nueva_tarea = {
        "title": "tarea_invalida_cero",
        "description": "desc",
        "priority": "alta",
        "effort_hours": 0,
        "status": "pendiente",
        "assigned_to": "usuario"
    }
    response = client.post("/tasks", json=nueva_tarea)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Verificamos que el error señale el campo effort_hours
    assert any(
        (isinstance(err.get("loc", []), list) and "effort_hours" in err.get("loc", []))
        for err in data["detail"]
    )


def test_crear_tarea_effort_hours_no_numerico(client):
    """
    Validar que 'effort_hours' no numérico produce error 422.
    """
    nueva_tarea = {
        "title": "tarea_invalida_no_numerico",
        "description": "desc",
        "priority": "media",
        "effort_hours": "abc",
        "status": "pendiente",
        "assigned_to": "usuario"
    }
    response = client.post("/tasks", json=nueva_tarea)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert any(
        (isinstance(err.get("loc", []), list) and "effort_hours" in err.get("loc", []))
        for err in data["detail"]
    )


def test_crear_tarea_effort_hours_token_invalido_json(client):
    """
    Enviar JSON inválido con token no citado para effort_hours
    y validar que el msg indique que debe ser numérico.
    """
    invalid_json = '{"title":"x","description":"y","priority":"alta","effort_hours": ew, "status":"pendiente","assigned_to":"z"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "effort_hours debe ser numérico" in data["msg"]
    # Confirma que es un error de JSON
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_crear_tarea_priority_invalida_msg(client):
    """
    Validar mensaje claro cuando priority no pertenece a los permitidos.
    """
    nueva_tarea = {
        "title": "tarea_invalida_priority",
        "description": "desc",
        "priority": "urgente",
        "effort_hours": 1.0,
        "status": "pendiente",
        "assigned_to": "usuario"
    }
    response = client.post("/tasks", json=nueva_tarea)
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "priority debe ser uno de:" in data["msg"]
    assert any(
        (isinstance(err.get("loc", []), list) and "priority" in err.get("loc", []))
        for err in data.get("detail", [])
    )


def test_crear_tarea_status_invalido_msg(client):
    """
    Validar mensaje claro cuando status no pertenece a los permitidos.
    """
    nueva_tarea = {
        "title": "tarea_invalida_status",
        "description": "desc",
        "priority": "alta",
        "effort_hours": 1.0,
        "status": "finalizada",
        "assigned_to": "usuario"
    }
    response = client.post("/tasks", json=nueva_tarea)
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "status debe ser uno de:" in data["msg"]
    assert any(
        (isinstance(err.get("loc", []), list) and "status" in err.get("loc", []))
        for err in data.get("detail", [])
    )


def test_crear_tarea_priority_token_invalido_json_string(client):
    """
    Enviar JSON inválido con valor de priority sin comillas dobles
    y validar mensaje de formato del campo.
    """
    invalid_json = '{"title":"x","description":"y","priority": urgente, "effort_hours": 1.0, "status":"pendiente","assigned_to":"z"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "priority tiene formato inválido: debe ser texto entre comillas dobles" in data["msg"]
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_crear_tarea_title_token_invalido_json_string(client):
    """
    Enviar JSON inválido con valor de title sin comillas dobles
    y validar mensaje de formato del campo.
    """
    invalid_json = '{"title": x, "description":"y","priority":"alta", "effort_hours": 1.0, "status":"pendiente","assigned_to":"z"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "title tiene formato inválido: debe ser texto entre comillas dobles" in data["msg"]
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_crear_tarea_status_token_invalido_json_string(client):
    """
    Enviar JSON inválido con valor de status sin comillas dobles
    y validar mensaje de formato del campo.
    """
    invalid_json = '{"title":"x","description":"y","priority":"alta", "effort_hours": 1.0, "status": pendiente, "assigned_to":"z"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "status tiene formato inválido: debe ser texto entre comillas dobles" in data["msg"]
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_priority_unquoted_but_effort_hours_numeric_no_wrong_msg(client):
    """
    JSON inválido por priority sin comillas, pero effort_hours es numérico válido.
    No debe agregarse el mensaje erróneo "effort_hours debe ser numérico" en msg.
    """
    invalid_json = '{"title":"x","description":"y","priority": alta, "effort_hours": 4.5, "status":"pendiente","assigned_to":"z"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "priority tiene formato inválido" in data["msg"]
    assert "effort_hours debe ser numérico" not in data["msg"]
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_crear_tarea_category_vacio_json_invalido(client):
    """
    Enviar JSON inválido con valor de category vacío (ej: "category": ,)
    y validar que el mensaje indique específicamente el campo category.
    """
    invalid_json = '{"assigned_to": "alex", "category": , "description": "descrpcion", "effort_hours": 4.5, "priority": "alta", "risk_analysis": "analisis_de_riesgos", "risk_mitigation": "plan_de_mitigacion", "status": "pendiente", "title": "tarea_de_ejemplo"}'
    response = client.post("/tasks", data=invalid_json, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    data = response.json()
    assert "msg" in data
    assert "category" in data["msg"]
    assert any(err.get("type") == "json_invalid" for err in data.get("detail", []))


def test_leer_todas_las_tareas(client):
    """
    Test para obtener todas las tareas mediante GET /tasks.
    """
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_leer_una_tarea(client):
    """
    Test para obtener una tarea por id con GET /tasks/{id}.
    """
    nueva_tarea = {
        "title": "tarea_para_leer",
        "description": "descripcion",
        "priority": "media",
        "effort_hours": 1.0,
        "status": "pendiente",
        "assigned_to": "usuario_leer",
    }
    post_response = client.post("/tasks", json=nueva_tarea)
    task_id = post_response.json()["id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == task_id


def test_actualizar_tarea(client):
    """
    Test para actualizar una tarea existente vía PUT /tasks/{id}.
    """
    nueva_tarea = {
        "title": "tarea_para_actualizar",
        "description": "descripcion",
        "priority": "baja",
        "effort_hours": 3.0,
        "status": "pendiente",
        "assigned_to": "usuario_actualizar",
    }
    post_response = client.post("/tasks", json=nueva_tarea)
    task_id = post_response.json()["id"]

    tarea_actualizada = {
        "title": "tarea_actualizada",
        "description": "descripcion_actualizada",
        "priority": "alta",
        "effort_hours": 5.0,
        "status": "en_progreso",
        "assigned_to": "usuario_actualizado",
    }
    put_response = client.put(f"/tasks/{task_id}", json=tarea_actualizada)
    assert put_response.status_code == 200
    data = put_response.json()
    assert data["title"] == tarea_actualizada["title"]
    assert data["status"] == tarea_actualizada["status"]


def test_eliminar_tarea(client):
    """
    Test para eliminar una tarea vía DELETE /tasks/{id} y validar inexistencia posterior.
    """
    nueva_tarea = {
        "title": "tarea_para_eliminar",
        "description": "descripcion",
        "priority": "bloqueante",
        "effort_hours": 8.0,
        "status": "pendiente",
        "assigned_to": "usuario_eliminar",
    }
    post_response = client.post("/tasks", json=nueva_tarea)
    task_id = post_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404



