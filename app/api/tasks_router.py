from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.task_schema import task_create, task_update, task_schema
from app.services.task_service import task_service


router = APIRouter()


@router.post(
    "/tasks",
    response_model=task_schema,
    status_code=status.HTTP_201_CREATED,
    summary="crear_una_tarea",
    responses={
        201: {
            "description": "tarea_creada",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "tarea_de_ejemplo",
                        "description": "descripcion_de_la_tarea",
                        "priority": "alta",
                        "effort_hours": 4.5,
                        "status": "pendiente",
                        "assigned_to": "juan_perez",
                        "created_at": "2026-02-20T10:00:00"
                    }
                }
            }
        }
    }
)
def crear_tarea(task_input: task_create, db: Session = Depends(get_db)):
    """
    Endpoint para crear una nueva tarea en base de datos.
    
    Args:
        task_input (task_create): Datos de la nueva tarea (sin id).
        db (Session): Sesión de base de datos inyectada.
    
    Returns:
        task_schema: La tarea creada (con id asignado).
    """
    try:
        return task_service.create_task(db, task_input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear tarea: {str(e)}"
        )


@router.get(
    "/tasks",
    response_model=List[task_schema],
    summary="leer_todas_las_tareas",
)
def leer_todas_las_tareas(db: Session = Depends(get_db)) -> List[task_schema]:
    """
    Devuelve la lista completa de tareas almacenadas en base de datos.
    
    Args:
        db (Session): Sesión de base de datos inyectada.
    
    Returns:
        List[task_schema]: Lista de tareas.
    """
    return task_service.get_all_tasks(db)


@router.get(
    "/tasks/{task_id}",
    response_model=task_schema,
    summary="leer_una_tarea",
)
def leer_tarea(task_id: int, db: Session = Depends(get_db)) -> task_schema:
    """
    Busca y devuelve una tarea por id desde la base de datos.
    
    Args:
        task_id (int): ID de la tarea a buscar.
        db (Session): Sesión de base de datos inyectada.
    
    Returns:
        task_schema: Si existe, la tarea encontrada.
    
    Raises:
        HTTPException(404): Si la tarea no existe.
    """
    existing_task = task_service.get_task(db, task_id)
    if existing_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tarea_no_encontrada",
        )
    return existing_task


@router.put(
    "/tasks/{task_id}",
    response_model=task_schema,
    summary="actualizar_una_tarea",
)
def actualizar_tarea(task_id: int, task_input: task_update, db: Session = Depends(get_db)) -> task_schema:
    """
    Actualiza una tarea existente por su id en la base de datos.
    
    Args:
        task_id (int): ID de la tarea a actualizar.
        task_input (task_update): Nuevos datos de la tarea (campos opcionales).
        db (Session): Sesión de base de datos inyectada.
    
    Returns:
        task_schema: Tarea actualizada.
    
    Raises:
        HTTPException(404): Si la tarea no existe.
    """
    try:
        updated = task_service.update_task(db, task_id, task_input)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="tarea_no_encontrada",
            )
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar tarea: {str(e)}"
        )


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="eliminar_una_tarea",
)
def eliminar_tarea(task_id: int, db: Session = Depends(get_db)) -> None:
    """
    Elimina una tarea existente de la base de datos.
    
    Args:
        task_id (int): ID de la tarea a eliminar.
        db (Session): Sesión de base de datos inyectada.
    
    Raises:
        HTTPException(404): Si la tarea no existe.
    """
    deleted = task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tarea_no_encontrada",
        )





