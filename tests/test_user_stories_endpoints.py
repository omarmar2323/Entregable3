"""
Tests para los endpoints de historias de usuario.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import fastapi_app
from app.database.database import Base, get_db
from app.database.models import user_story, task


# Base de datos en memoria para tests con StaticPool
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
    fastapi_app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Fixture que proporciona el cliente de FastAPI."""
    return TestClient(fastapi_app)


@pytest.fixture
def sample_user_story(test_db):
    """Fixture que crea una historia de usuario de prueba."""
    db = TestingSessionLocal()
    try:
        story = user_story(
            project="Proyecto Test",
            role="usuario",
            goal="realizar pruebas",
            reason="validar funcionalidad",
            description="Historia de usuario de prueba para testing",
            priority="media",
            story_points=3,
            effort_hours=8.0
        )
        db.add(story)
        db.commit()
        db.refresh(story)
        return story
    finally:
        db.close()


def test_get_user_stories_page(client):
    """Test para obtener la página de historias de usuario."""
    response = client.get("/user-stories")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_get_user_stories_page_with_data(client, sample_user_story):
    """Test para obtener la página con historias existentes."""
    response = client.get("/user-stories")
    assert response.status_code == 200
    assert "Proyecto Test" in response.text


def test_get_user_story_tasks_page(client, sample_user_story):
    """Test para obtener la página de tareas de una historia."""
    response = client.get(f"/user-stories/{sample_user_story.id}/tasks")
    assert response.status_code == 200
    assert "Historia de Usuario" in response.text
    assert "Proyecto Test" in response.text


def test_get_user_story_tasks_page_not_found(client):
    """Test para obtener tareas de una historia inexistente."""
    response = client.get("/user-stories/9999/tasks")
    assert response.status_code == 404


def test_create_user_story_from_prompt_mock(client, monkeypatch):
    """Test para crear una historia desde un prompt (mock de IA)."""
    from app.models.user_story_schema import user_story_create
    
    # Mock del servicio de IA (acepta todos los argumentos del método real)
    def mock_generate_user_story(prompt, db=None):
        return user_story_create(
            project="Mock Project",
            role="usuario_test",
            goal="objetivo_test",
            reason="razon_test",
            description="descripcion_test",
            priority="alta",
            story_points=5,
            effort_hours=12.0
        )
    
    # Hacer patch en el lugar donde se usa (el router)
    import app.api.user_stories_router as router_module
    monkeypatch.setattr(
        router_module.ai_user_story_service,
        "generate_user_story",
        mock_generate_user_story
    )
    
    # Usar follow_redirects=False para capturar el redirect
    response = client.post(
        "/user-stories",
        data={"prompt": "Necesito un sistema de login"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    
    # Debe redireccionar después de crear
    assert response.status_code == 303
    assert response.headers["location"] == "/user-stories"


def test_generate_tasks_for_user_story_mock(client, sample_user_story, monkeypatch):
    """Test para generar tareas para una historia (mock completo de IA)."""
    from app.models.task_model import task as task_model
    
    # Mock del servicio de IA para generar tareas (acepta todos los argumentos del método real)
    def mock_generate_tasks(user_story_data, category, num_tasks=4, existing_tasks=None):
        return [
            {
                "title": f"Tarea Test {i}",
                "description": f"Descripción de tarea {i} para testing con más de 50 caracteres para evitar llamadas LLM",
                "priority": "media",
                "effort_hours": 4.0,
                "status": "pendiente",
                "assigned_to": "developer",
                "category": category
            }
            for i in range(num_tasks)
        ]
    
    # Mock para determine_category_from_description
    def mock_determine_category(story_dict, db=None):
        return "Backend"
    
    # Mock para generar descripción (devuelve el mismo objeto sin cambios)
    def mock_generate_description(task_obj):
        return task_obj
    
    # Mock para estimar esfuerzo (devuelve el mismo objeto)
    def mock_estimate_effort(task_obj):
        if not task_obj.effort_hours:
            task_obj.effort_hours = 4.0
        return task_obj
    
    # Mock para auditar riesgos (devuelve el mismo objeto)
    def mock_audit_task(task_obj):
        task_obj.risk_analysis = "Análisis de riesgos mock"
        task_obj.risk_mitigation = "Plan de mitigación mock"
        return task_obj
    
    # Hacer patch en el lugar donde se usa (el router)
    import app.api.user_stories_router as router_module
    monkeypatch.setattr(
        router_module.ai_user_story_service,
        "generate_tasks_for_story",
        mock_generate_tasks
    )
    monkeypatch.setattr(
        router_module.ai_user_story_service,
        "determine_category_from_description",
        mock_determine_category
    )
    monkeypatch.setattr(
        router_module.llm_service,
        "generate_description",
        mock_generate_description
    )
    monkeypatch.setattr(
        router_module.llm_service,
        "estimate_effort",
        mock_estimate_effort
    )
    monkeypatch.setattr(
        router_module.llm_service,
        "audit_task",
        mock_audit_task
    )
    
    # Usar follow_redirects=False para capturar el redirect
    response = client.post(
        f"/user-stories/{sample_user_story.id}/generate-tasks",
        follow_redirects=False
    )
    
    # Debe redireccionar a la página de tareas
    assert response.status_code == 303
    assert f"/user-stories/{sample_user_story.id}/tasks" in response.headers["location"]
    
    # Verificar que se crearon las tareas
    db = TestingSessionLocal()
    try:
        tasks = db.query(task).filter(task.user_story_id == sample_user_story.id).all()
        assert len(tasks) == 4  # El mock genera 4 tareas por defecto
    finally:
        db.close()


def test_generate_tasks_for_nonexistent_story(client):
    """Test para generar tareas para una historia que no existe."""
    response = client.post("/user-stories/9999/generate-tasks")
    assert response.status_code == 404
