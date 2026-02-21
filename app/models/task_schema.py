"""
Esquemas Pydantic para validación de datos de tareas.
Actualizado para trabajar con base de datos.
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


# Tipos de prioridad y estado
priority_type = Literal["baja", "media", "alta", "bloqueante"]
status_type = Literal["pendiente", "en_progreso", "en_revision", "completada"]


class task_base(BaseModel):
    """
    Esquema base para tareas.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    description: str = Field(default="", description="Descripción detallada")
    priority: priority_type = Field(default="media", description="Prioridad de la tarea")
    effort_hours: Optional[float] = Field(None, gt=0.0, description="Horas estimadas (debe ser mayor que 0)")
    status: status_type = Field(default="pendiente", description="Estado de la tarea")
    assigned_to: str = Field(..., min_length=1, max_length=100, description="Persona asignada")
    category: Optional[str] = Field(None, description="Nombre de categoría (se resuelve a ID en BD)")
    risk_analysis: Optional[str] = Field(None, description="Análisis de riesgos")
    risk_mitigation: Optional[str] = Field(None, description="Plan de mitigación")
    user_story_id: Optional[int] = Field(None, description="ID de historia de usuario asociada")

    @field_validator("category", "risk_analysis", "risk_mitigation", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte strings vacíos a None para campos opcionales."""
        if v == "":
            return None
        return v


class task_create(task_base):
    """
    Esquema para crear una nueva tarea.
    El campo 'category' es el nombre de categoría (string).
    Se resuelve a category_id en el servicio.
    """
    pass


class task_update(BaseModel):
    """
    Esquema para actualizar una tarea existente.
    Todos los campos son opcionales.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[priority_type] = None
    effort_hours: Optional[float] = Field(None, gt=0.0)
    status: Optional[status_type] = None
    assigned_to: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = None
    risk_analysis: Optional[str] = None
    risk_mitigation: Optional[str] = None
    user_story_id: Optional[int] = None

    @field_validator("category", "risk_analysis", "risk_mitigation", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte strings vacíos a None para campos opcionales."""
        if v == "":
            return None
        return v


class task_schema(task_base):
    """
    Esquema completo de tarea (incluye ID y timestamp).
    Se usa para respuestas de la API.
    """
    id: int
    created_at: datetime

    @field_validator("priority", "status", mode="before")
    @classmethod
    def convert_enum_to_string(cls, v):
        """Convierte objetos Enum de SQLAlchemy a sus valores string."""
        if hasattr(v, "value"):  # Es un Enum
            return v.value
        return v

    class Config:
        from_attributes = True

class task_schemas(BaseModel):
    """
    Esquema para lista de tareas.
    """
    tasks: List[task_schema] = []
