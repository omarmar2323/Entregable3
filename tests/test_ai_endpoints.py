"""
Tests para los endpoints de IA relacionados con tareas.

Este módulo contiene pruebas unitarias para los endpoints:
- POST /ai/tasks/describe
- POST /ai/tasks/categorize
- POST /ai/tasks/estimate
- POST /ai/tasks/audit
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, fastapi_app
from app.models.task_model import task
from app.database.database import Base, get_db
from app.database.models import category


# Base de datos en memoria para tests de TestTaskModelNewFields
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dependencia get_db para tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


client = TestClient(app)


# Datos de prueba base
def get_sample_task() -> dict:
    """Retorna una tarea de ejemplo para pruebas."""
    return {
        "title": "implementar_modulo_autenticacion",
        "description": "",
        "priority": "alta",
        "effort_hours": None,
        "status": "pendiente",
        "assigned_to": "desarrollador_senior",
        "category": None,
        "risk_analysis": None,
        "risk_mitigation": None
    }


def get_complete_task() -> dict:
    """Retorna una tarea completa para pruebas de auditoría."""
    return {
        "title": "desplegar_microservicio_produccion",
        "description": "Desplegar el microservicio de autenticación en el cluster de producción",
        "priority": "bloqueante",
        "effort_hours": 8.0,
        "status": "pendiente",
        "assigned_to": "devops_engineer",
        "category": "DevOps",
        "risk_analysis": None,
        "risk_mitigation": None
    }


class TestGenerateDescription:
    """Tests para el endpoint POST /ai/tasks/describe"""
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_generar_descripcion_exitosa(self, mock_llm):
        """Test para validar generación de descripción exitosa."""
        mock_llm.return_value = "Esta tarea consiste en implementar un módulo de autenticación robusto que permita a los usuarios iniciar sesión de forma segura."
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/describe", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "description" in data
        assert data["description"] != ""
        assert data["title"] == task_data["title"]
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_generar_descripcion_mantiene_otros_campos(self, mock_llm):
        """Test para validar que los demás campos se mantienen intactos."""
        mock_llm.return_value = "Descripción generada por IA"
        
        task_data = get_sample_task()
        task_data["priority"] = "media"
        task_data["assigned_to"] = "usuario_test"
        
        response = client.post("/ai/tasks/describe", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == "media"
        assert data["assigned_to"] == "usuario_test"
    
    @patch('app.services.llm_service.llm_service._get_client')
    def test_generar_descripcion_error_llm(self, mock_client):
        """Test para validar manejo de errores del LLM."""
        mock_client.side_effect = Exception("Error de conexión")
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/describe", json=task_data)
        
        assert response.status_code == 500
        assert "error_al_generar_descripcion" in response.json()["detail"]


class TestCategorizeTask:
    """Tests para el endpoint POST /ai/tasks/categorize"""
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_categorizar_tarea_exitosa(self, mock_llm):
        """Test para validar categorización exitosa."""
        mock_llm.return_value = "Backend"
        
        task_data = get_sample_task()
        task_data["description"] = "Implementar endpoint REST para autenticación"
        
        response = client.post("/ai/tasks/categorize", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert data["category"] == "Backend"
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_categorizar_tarea_categoria_testing(self, mock_llm):
        """Test para validar categorización como Testing."""
        mock_llm.return_value = "Testing"
        
        task_data = get_sample_task()
        task_data["title"] = "crear_tests_unitarios_api"
        task_data["description"] = "Crear tests unitarios para validar la API"
        
        response = client.post("/ai/tasks/categorize", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "Testing"
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_categorizar_tarea_categoria_invalida_usa_default(self, mock_llm):
        """Test para validar que categoría inválida se maneja correctamente."""
        mock_llm.return_value = "CategoriaInexistente"
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/categorize", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        # Debería asignar Backend por defecto
        assert data["category"] == "Backend"
    
    @patch('app.services.llm_service.llm_service._get_client')
    def test_categorizar_tarea_error_llm(self, mock_client):
        """Test para validar manejo de errores del LLM."""
        mock_client.side_effect = Exception("Error de conexión")
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/categorize", json=task_data)
        
        assert response.status_code == 500
        assert "error_al_categorizar_tarea" in response.json()["detail"]


class TestEstimateEffort:
    """Tests para el endpoint POST /ai/tasks/estimate"""
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_estimar_esfuerzo_exitoso(self, mock_llm):
        """Test para validar estimación exitosa."""
        mock_llm.return_value = "16.5"
        
        task_data = get_sample_task()
        task_data["description"] = "Implementar sistema completo de autenticación"
        task_data["category"] = "Backend"
        
        response = client.post("/ai/tasks/estimate", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "effort_hours" in data
        assert data["effort_hours"] == 16.5
        assert isinstance(data["effort_hours"], float)
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_estimar_esfuerzo_respuesta_con_texto(self, mock_llm):
        """Test para validar parsing cuando LLM incluye texto."""
        mock_llm.return_value = "Estimo que tomará aproximadamente 8.5 horas"
        
        task_data = get_sample_task()
        task_data["description"] = "Crear endpoint simple"
        
        response = client.post("/ai/tasks/estimate", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["effort_hours"] == 8.5
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_estimar_esfuerzo_respuesta_invalida_usa_default(self, mock_llm):
        """Test para validar valor por defecto cuando parsing falla."""
        mock_llm.return_value = "No puedo estimar"
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/estimate", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["effort_hours"] == 4.0  # Valor por defecto
    
    @patch('app.services.llm_service.llm_service._get_client')
    def test_estimar_esfuerzo_error_llm(self, mock_client):
        """Test para validar manejo de errores del LLM."""
        mock_client.side_effect = Exception("Error de conexión")
        
        task_data = get_sample_task()
        response = client.post("/ai/tasks/estimate", json=task_data)
        
        assert response.status_code == 500
        assert "error_al_estimar_esfuerzo" in response.json()["detail"]


class TestAuditRisks:
    """Tests para el endpoint POST /ai/tasks/audit"""
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_auditar_riesgos_exitoso(self, mock_llm):
        """Test para validar auditoría exitosa."""
        mock_llm.side_effect = [
            "Riesgos identificados: 1. Posible tiempo de inactividad durante el despliegue. 2. Incompatibilidad con versiones anteriores.",
            "Plan de mitigación: 1. Implementar blue-green deployment. 2. Realizar pruebas exhaustivas en staging."
        ]
        
        task_data = get_complete_task()
        response = client.post("/ai/tasks/audit", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_analysis" in data
        assert "risk_mitigation" in data
        assert data["risk_analysis"] != ""
        assert data["risk_mitigation"] != ""
        assert "Riesgos" in data["risk_analysis"]
        assert "mitigación" in data["risk_mitigation"]
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_auditar_riesgos_mantiene_otros_campos(self, mock_llm):
        """Test para validar que los demás campos se mantienen."""
        mock_llm.side_effect = [
            "Análisis de riesgos completado",
            "Plan de mitigación completado"
        ]
        
        task_data = get_complete_task()
        response = client.post("/ai/tasks/audit", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["category"] == task_data["category"]
        assert data["effort_hours"] == task_data["effort_hours"]
    
    @patch('app.services.llm_service.llm_service._call_llm')
    def test_auditar_realiza_dos_llamadas_llm(self, mock_llm):
        """Test para validar que se realizan dos llamadas al LLM."""
        mock_llm.side_effect = [
            "Primer análisis",
            "Segundo análisis (mitigación)"
        ]
        
        task_data = get_complete_task()
        response = client.post("/ai/tasks/audit", json=task_data)
        
        assert response.status_code == 200
        assert mock_llm.call_count == 2
    
    @patch('app.services.llm_service.llm_service._get_client')
    def test_auditar_riesgos_error_llm(self, mock_client):
        """Test para validar manejo de errores del LLM."""
        mock_client.side_effect = Exception("Error de conexión")
        
        task_data = get_complete_task()
        response = client.post("/ai/tasks/audit", json=task_data)
        
        assert response.status_code == 500
        assert "error_al_auditar_riesgos" in response.json()["detail"]


class TestTaskModelNewFields:
    """
    Tests para validar los nuevos campos del modelo Task.
    
    NOTA: Estos tests requieren una base de datos real con tablas y categorías.
    Se han simplificado para validar el esquema sin interacción con BD.
    """
    
    def test_task_schema_con_todos_los_campos(self):
        """Test para validar que el esquema acepta todos los campos."""
        from app.models.task_schema import task_create
        
        task_data = {
            "title": "tarea_completa",
            "description": "descripcion completa",
            "priority": "alta",
            "effort_hours": 10.0,
            "status": "pendiente",
            "assigned_to": "usuario",
            "category": "Backend",
            "risk_analysis": "analisis de riesgos",
            "risk_mitigation": "plan de mitigacion"
        }
        
        # Validar que el esquema acepta los datos
        task_obj = task_create(**task_data)
        assert task_obj.title == "tarea_completa"
        assert task_obj.category == "Backend"
        assert task_obj.risk_analysis == "analisis de riesgos"
        assert task_obj.risk_mitigation == "plan de mitigacion"
    
    def test_task_schema_sin_campos_opcionales(self):
        """Test para validar que el esquema funciona sin campos opcionales."""
        from app.models.task_schema import task_create
        
        task_data = {
            "title": "tarea_simple",
            "description": "descripcion",
            "priority": "media",
            "effort_hours": 5.0,
            "status": "pendiente",
            "assigned_to": "usuario"
        }
        
        # Validar que el esquema acepta los datos sin campos opcionales
        task_obj = task_create(**task_data)
        assert task_obj.category is None
        assert task_obj.risk_analysis is None
        assert task_obj.risk_mitigation is None
    
    def test_task_schema_categoria_como_string(self):
        """Test para validar que category acepta cualquier string."""
        from app.models.task_schema import task_create
        
        task_data = {
            "title": "tarea_test",
            "description": "descripcion",
            "priority": "alta",
            "effort_hours": 5.0,
            "status": "pendiente",
            "assigned_to": "usuario",
            "category": "CualquierCategoria"
        }
        
        # El esquema acepta cualquier string, la validación de existencia
        # se hace en el servicio contra la BD
        task_obj = task_create(**task_data)
        assert task_obj.category == "CualquierCategoria"
    
    def test_task_schema_categorias_tipicas(self):
        """Test para validar que el esquema acepta las categorías típicas."""
        from app.models.task_schema import task_create
        
        categorias_validas = [
            "Frontend", "Backend", "Testing", "Infra", "DevOps",
            "Database", "Security", "API", "UI_UX", "Documentation",
            "Architecture", "Mobile", "Cloud", "Analytics"
        ]
        
        for categoria in categorias_validas:
            task_data = {
                "title": f"tarea_{categoria.lower()}",
                "description": "descripcion",
                "priority": "media",
                "effort_hours": 5.0,
                "status": "pendiente",
                "assigned_to": "usuario",
                "category": categoria
            }
            
            task_obj = task_create(**task_data)
            assert task_obj.category == categoria, f"Falló para categoría: {categoria}"
