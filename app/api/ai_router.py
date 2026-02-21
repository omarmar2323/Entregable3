"""
Router para endpoints de IA relacionados con tareas.

Este módulo contiene los endpoints que utilizan LLM para:
- Generar descripciones
- Categorizar tareas
- Estimar esfuerzo
- Auditar riesgos
"""

from fastapi import APIRouter, HTTPException, status

from app.models.task_model import task, task_ai_input
from app.services.llm_service import llm_service


router = APIRouter(prefix="/ai/tasks", tags=["AI Tasks"])


@router.post(
    "/describe",
    response_model=task,
    status_code=status.HTTP_200_OK,
    summary="generar_descripcion_con_ia",
    responses={
        200: {
            "description": "descripcion_generada",
            "content": {
                "application/json": {
                    "example": {
                        "id": None,
                        "title": "implementar_autenticacion_jwt",
                        "description": "Implementar un sistema de autenticación basado en JWT...",
                        "priority": "alta",
                        "effort_hours": None,
                        "status": "pendiente",
                        "assigned_to": "desarrollador_backend",
                        "category": None,
                        "risk_analysis": None,
                        "risk_mitigation": None
                    }
                }
            }
        },
        500: {
            "description": "error_al_generar_descripcion"
        }
    }
)
def generar_descripcion(task_input: task_ai_input) -> task:
    """
    Genera una descripción para la tarea usando IA.
    
    Recibe una tarea con description vacía y genera su description
    con LLM a partir del resto de campos como el title.
    
    Args:
        task_input (task_ai_input): Tarea con description vacía o a regenerar.
        
    Returns:
        task: La tarea con el campo description completado por IA.
    """
    try:
        return llm_service.generate_description(task_input.to_task())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error_al_generar_descripcion: {str(e)}"
        )


@router.post(
    "/categorize",
    response_model=task,
    status_code=status.HTTP_200_OK,
    summary="categorizar_tarea_con_ia",
    responses={
        200: {
            "description": "tarea_categorizada",
            "content": {
                "application/json": {
                    "example": {
                        "id": None,
                        "title": "crear_tests_unitarios",
                        "description": "Crear tests unitarios para el módulo de usuarios",
                        "priority": "media",
                        "effort_hours": 8.0,
                        "status": "pendiente",
                        "assigned_to": "qa_engineer",
                        "category": "Testing",
                        "risk_analysis": None,
                        "risk_mitigation": None
                    }
                }
            }
        },
        500: {
            "description": "error_al_categorizar_tarea"
        }
    }
)
def categorizar_tarea(task_input: task_ai_input) -> task:
    """
    Categoriza la tarea usando IA.
    
    Recibe una tarea sin categoría y con LLM la clasifica bajo una categoría:
    Frontend, Backend, Testing, Infra, DevOps, Database, Security, API,
    UI_UX, Documentation, Architecture, Mobile, Cloud, Analytics.
    
    Args:
        task_input (task_ai_input): Tarea sin categoría asignada.
        
    Returns:
        task: La tarea con el campo category completado por IA.
    """
    try:
        # Convertir a task estricto (valores inválidos se convierten a None)
        strict_task = task_input.to_task()
        return llm_service.categorize_task(strict_task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error_al_categorizar_tarea: {str(e)}"
        )


@router.post(
    "/estimate",
    response_model=task,
    status_code=status.HTTP_200_OK,
    summary="estimar_esfuerzo_con_ia",
    responses={
        200: {
            "description": "esfuerzo_estimado",
            "content": {
                "application/json": {
                    "example": {
                        "id": None,
                        "title": "migrar_base_de_datos",
                        "description": "Migrar la base de datos de PostgreSQL a MongoDB",
                        "priority": "alta",
                        "effort_hours": 24.0,
                        "status": "pendiente",
                        "assigned_to": "dba",
                        "category": "Database",
                        "risk_analysis": None,
                        "risk_mitigation": None
                    }
                }
            }
        },
        500: {
            "description": "error_al_estimar_esfuerzo"
        }
    }
)
def estimar_esfuerzo(task_input: task_ai_input) -> task:
    """
    Estima el esfuerzo en horas para la tarea usando IA.
    
    Siempre genera una nueva estimación con IA, ignorando cualquier valor
    previo en effort_hours. Esto permite re-estimar tareas existentes.
    
    Args:
        task_input (task_ai_input): Tarea a estimar (effort_hours será ignorado).
        
    Returns:
        task: La tarea con el campo effort_hours completado por IA (valor numérico).
    """
    try:
        # Convertir a task estricto (effort_hours inválidos se convierten a None)
        strict_task = task_input.to_task()
        # Forzar effort_hours a None para que siempre se estime con IA
        strict_task.effort_hours = None
        return llm_service.estimate_effort(strict_task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error_al_estimar_esfuerzo: {str(e)}")


@router.post(
    "/audit",
    response_model=task,
    status_code=status.HTTP_200_OK,
    summary="auditar_riesgos_con_ia",
    responses={
        200: {
            "description": "auditoria_completada",
            "content": {
                "application/json": {
                    "example": {
                        "id": None,
                        "title": "desplegar_en_produccion",
                        "description": "Desplegar la nueva versión de la aplicación en producción",
                        "priority": "bloqueante",
                        "effort_hours": 4.0,
                        "status": "pendiente",
                        "assigned_to": "devops_engineer",
                        "category": "DevOps",
                        "risk_analysis": "Riesgos identificados: 1. Posible tiempo de inactividad...",
                        "risk_mitigation": "Plan de mitigación: 1. Implementar blue-green deployment..."
                    }
                }
            }
        },
        500: {
            "description": "error_al_auditar_riesgos"
        }
    }
)
def auditar_riesgos(task_input: task_ai_input) -> task:
    """
    Realiza análisis de riesgos y genera plan de mitigación usando IA.
    
    Recibe una tarea con todos los campos rellenos menos risk_analysis
    y risk_mitigation. Utiliza LLM para:
    1. Generar un análisis de riesgos (risk_analysis)
    2. Generar un plan de mitigación basado en el análisis (risk_mitigation)
    
    Args:
        task_input (task_ai_input): Tarea sin risk_analysis ni risk_mitigation.
        
    Returns:
        task: La tarea con risk_analysis y risk_mitigation completados por IA.
    """
    try:
        # Convertir a task estricto
        strict_task = task_input.to_task()
        return llm_service.audit_task(strict_task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"error_al_auditar_riesgos: {str(e)}")
