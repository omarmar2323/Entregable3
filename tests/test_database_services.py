"""
Tests para los servicios de base de datos.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import user_story, task
from app.services.user_story_service import user_story_service
from app.services.task_service import task_service
from app.models.user_story_schema import user_story_create, user_story_update
from app.models.task_schema import task_create, task_update


# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_services.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fixture que crea y destruye la base de datos para cada test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# Tests para user_story_service
def test_create_user_story(db):
    """Test para crear una historia de usuario."""
    story_data = user_story_create(
        project="Test Project",
        role="usuario",
        goal="completar pruebas",
        reason="asegurar calidad",
        description="Historia de prueba",
        priority="alta",
        story_points=5,
        effort_hours=10.0
    )
    
    created = user_story_service.create_user_story(db, story_data)
    
    assert created.id is not None
    assert created.project == "Test Project"
    assert created.role == "usuario"
    assert created.goal == "completar pruebas"


def test_get_user_story(db):
    """Test para obtener una historia de usuario por ID."""
    story_data = user_story_create(
        project="Test Project",
        role="usuario",
        goal="test goal",
        reason="test reason",
        description="test description",
        priority="media",
        story_points=3,
        effort_hours=8.0
    )
    created = user_story_service.create_user_story(db, story_data)
    
    retrieved = user_story_service.get_user_story(db, created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.project == "Test Project"


def test_get_all_user_stories(db):
    """Test para obtener todas las historias de usuario."""
    # Crear varias historias
    for i in range(3):
        story_data = user_story_create(
            project=f"Project {i}",
            role="usuario",
            goal=f"goal {i}",
            reason=f"reason {i}",
            description=f"description {i}",
            priority="media",
            story_points=i+1,
            effort_hours=float(i+1)*2
        )
        user_story_service.create_user_story(db, story_data)
    
    all_stories = user_story_service.get_all_user_stories(db)
    assert len(all_stories) == 3


def test_update_user_story(db):
    """Test para actualizar una historia de usuario."""
    story_data = user_story_create(
        project="Original Project",
        role="usuario",
        goal="original goal",
        reason="original reason",
        description="original description",
        priority="baja",
        story_points=2,
        effort_hours=4.0
    )
    created = user_story_service.create_user_story(db, story_data)
    
    update_data = user_story_update(
        project="Updated Project",
        priority="alta",
        story_points=8
    )
    
    updated = user_story_service.update_user_story(db, created.id, update_data)
    
    assert updated is not None
    assert updated.project == "Updated Project"
    assert updated.priority.value == "alta"
    assert updated.story_points == 8
    assert updated.goal == "original goal"  # No modificado


def test_delete_user_story(db):
    """Test para eliminar una historia de usuario."""
    story_data = user_story_create(
        project="To Delete",
        role="usuario",
        goal="delete goal",
        reason="delete reason",
        description="delete description",
        priority="media",
        story_points=3,
        effort_hours=6.0
    )
    created = user_story_service.create_user_story(db, story_data)
    
    deleted = user_story_service.delete_user_story(db, created.id)
    assert deleted is True
    
    retrieved = user_story_service.get_user_story(db, created.id)
    assert retrieved is None


# Tests para task_service
def test_create_task(db):
    """Test para crear una tarea."""
    task_data = task_create(
        title="Test Task",
        description="Test description",
        priority="alta",
        effort_hours=5.0,
        status="pendiente",
        assigned_to="developer",
        category="Backend"
    )
    
    created = task_service.create_task(db, task_data)
    
    assert created.id is not None
    assert created.title == "Test Task"
    assert created.priority.value == "alta"


def test_get_task(db):
    """Test para obtener una tarea por ID."""
    task_data = task_create(
        title="Get Task Test",
        description="description",
        priority="media",
        effort_hours=3.0,
        status="pendiente",
        assigned_to="tester",
        category="Testing"
    )
    created = task_service.create_task(db, task_data)
    
    retrieved = task_service.get_task(db, created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Get Task Test"


def test_get_tasks_by_user_story(db):
    """Test para obtener tareas asociadas a una historia."""
    # Crear historia
    story_data = user_story_create(
        project="Task Parent",
        role="usuario",
        goal="test",
        reason="test",
        description="test",
        priority="media",
        story_points=3,
        effort_hours=6.0
    )
    story = user_story_service.create_user_story(db, story_data)
    
    # Crear tareas asociadas
    for i in range(3):
        task_data = task_create(
            title=f"Task {i}",
            description=f"desc {i}",
            priority="media",
            status="pendiente",
            assigned_to="dev",
            user_story_id=story.id
        )
        task_service.create_task(db, task_data)
    
    tasks = task_service.get_tasks_by_user_story(db, story.id)
    assert len(tasks) == 3


def test_update_task(db):
    """Test para actualizar una tarea."""
    task_data = task_create(
        title="Original Task",
        description="original",
        priority="baja",
        status="pendiente",
        assigned_to="dev1"
    )
    created = task_service.create_task(db, task_data)
    
    update_data = task_update(
        title="Updated Task",
        priority="bloqueante",
        status="en_progreso",
        assigned_to="dev2"
    )
    
    updated = task_service.update_task(db, created.id, update_data)
    
    assert updated is not None
    assert updated.title == "Updated Task"
    assert updated.priority.value == "bloqueante"
    assert updated.status.value == "en_progreso"
    assert updated.assigned_to == "dev2"


def test_delete_task(db):
    """Test para eliminar una tarea."""
    task_data = task_create(
        title="To Delete",
        description="delete",
        priority="media",
        status="pendiente",
        assigned_to="dev"
    )
    created = task_service.create_task(db, task_data)
    
    deleted = task_service.delete_task(db, created.id)
    assert deleted is True
    
    retrieved = task_service.get_task(db, created.id)
    assert retrieved is None


def test_delete_user_story_cascades_tasks(db):
    """Test para verificar que eliminar una historia elimina sus tareas (cascade)."""
    # Crear historia
    story_data = user_story_create(
        project="Cascade Test",
        role="usuario",
        goal="test",
        reason="test",
        description="test",
        priority="media",
        story_points=3,
        effort_hours=6.0
    )
    story = user_story_service.create_user_story(db, story_data)
    
    # Crear tareas asociadas
    task_ids = []
    for i in range(3):
        task_data = task_create(
            title=f"Task {i}",
            description=f"desc {i}",
            priority="media",
            status="pendiente",
            assigned_to="dev",
            user_story_id=story.id
        )
        created_task = task_service.create_task(db, task_data)
        task_ids.append(created_task.id)
    
    # Eliminar historia
    user_story_service.delete_user_story(db, story.id)
    
    # Verificar que las tareas también se eliminaron
    for task_id in task_ids:
        retrieved = task_service.get_task(db, task_id)
        assert retrieved is None
