"""
Esquemas Pydantic para validación de datos de historias de usuario.
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


# Enums para prioridad
priority_type = Literal["baja", "media", "alta", "bloqueante"]


class user_story_base(BaseModel):
    """
    Esquema base para historias de usuario.
    """
    project: str = Field(..., min_length=1, max_length=200, description="Nombre del proyecto")
    role: str = Field(..., min_length=1, max_length=200, description="Rol de usuario")
    goal: str = Field(..., min_length=1, max_length=500, description="Objetivo de la historia")
    reason: str = Field(..., min_length=1, max_length=500, description="Razón de la historia")
    description: str = Field(..., description="Descripción completa de la historia de usuario")
    priority: priority_type = Field(default="media", description="Prioridad")
    story_points: int = Field(default=1, ge=1, le=8, description="Puntos de historia (1-8)")
    effort_hours: float = Field(default=0.0, ge=0.0, description="Horas estimadas")
    tasks_total_hours: float = Field(default=0.0, ge=0.0, description="Suma total de horas de tareas asociadas")


class user_story_create(user_story_base):
    """
    Esquema para crear una nueva historia de usuario.
    """
    pass


class user_story_update(BaseModel):
    """
    Esquema para actualizar una historia de usuario existente.
    Todos los campos son opcionales.
    """
    project: Optional[str] = Field(None, min_length=1, max_length=200)
    role: Optional[str] = Field(None, min_length=1, max_length=200)
    goal: Optional[str] = Field(None, min_length=1, max_length=500)
    reason: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[priority_type] = None
    story_points: Optional[int] = Field(None, ge=1, le=8)
    effort_hours: Optional[float] = Field(None, ge=0.0)
    tasks_total_hours: Optional[float] = Field(None, ge=0.0)


class user_story_schema(user_story_base):
    """
    Esquema completo de historia de usuario (incluye ID y timestamp).
    Se usa para respuestas de la API.
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class user_story_schemas(BaseModel):
    """
    Esquema para lista de historias de usuario.
    """
    user_stories: List[user_story_schema] = []


class user_story_prompt(BaseModel):
    """
    Esquema para recibir un prompt y generar historia de usuario con IA.
    """
    prompt: str = Field(..., min_length=10, description="Prompt para generar historia de usuario")
