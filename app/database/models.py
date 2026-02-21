"""
Modelos SQLAlchemy para base de datos MySQL.
Define las tablas UserStory, Task y Category.
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum


class PriorityEnum(enum.Enum):
    """Enumeración para prioridades."""
    baja = "baja"
    media = "media"
    alta = "alta"
    bloqueante = "bloqueante"


class StatusEnum(enum.Enum):
    """Enumeración para estados de tareas."""
    pendiente = "pendiente"
    en_progreso = "en_progreso"
    en_revision = "en_revision"
    completada = "completada"


class category(Base):
    """
    Modelo ORM para categorías de tareas.
    
    Attributes:
        id: Clave primaria autoincremental
        name: Nombre de la categoría
        description: Descripción de la categoría
        created_at: Fecha de creación (automática)
        tasks: Relación con tareas asociadas
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación one-to-many con Task
    tasks = relationship("task", back_populates="category_rel")


class user_story(Base):
    """
    Modelo ORM para historias de usuario.
    
    Attributes:
        id: Clave primaria autoincremental
        project: Nombre del proyecto
        role: Rol de usuario en la historia
        goal: Objetivo de la historia de usuario
        reason: Razón de la historia de usuario
        description: Descripción completa de la historia
        priority: Prioridad (baja, media, alta, bloqueante)
        story_points: Puntos de historia estimados (1-8)
        effort_hours: Horas estimadas para completar
        created_at: Fecha de creación (automática)
        tasks: Relación con tareas asociadas
    """
    __tablename__ = "user_stories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    project = Column(String(200), nullable=False, index=True)
    role = Column(String(200), nullable=False)
    goal = Column(String(500), nullable=False)
    reason = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(
        Enum(PriorityEnum),
        nullable=False,
        default=PriorityEnum.media
    )
    story_points = Column(Integer, nullable=False, default=1)
    effort_hours = Column(Float, nullable=False, default=0.0)
    tasks_total_hours = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación one-to-many con Task
    tasks = relationship("task", back_populates="user_story", cascade="all, delete-orphan")


class task(Base):
    """
    Modelo ORM para tareas.
    
    Attributes:
        id: Clave primaria autoincremental
        title: Título de la tarea
        description: Descripción detallada
        priority: Prioridad de la tarea
        effort_hours: Horas estimadas
        status: Estado de la tarea
        assigned_to: Persona asignada
        category_id: Clave foránea a categoría
        risk_analysis: Análisis de riesgos
        risk_mitigation: Plan de mitigación
        user_story_id: Clave foránea a UserStory
        created_at: Fecha de creación (automática)
        user_story: Relación con historia de usuario
        category_rel: Relación con categoría
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    priority = Column(
        Enum(PriorityEnum),
        nullable=False,
        default=PriorityEnum.media
    )
    effort_hours = Column(Float, nullable=True)
    status = Column(
        Enum(StatusEnum),
        nullable=False,
        default=StatusEnum.pendiente
    )
    assigned_to = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    risk_analysis = Column(Text, nullable=True)
    risk_mitigation = Column(Text, nullable=True)
    user_story_id = Column(Integer, ForeignKey("user_stories.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relación many-to-one con UserStory
    user_story = relationship("user_story", back_populates="tasks")
    
    # Relación many-to-one con Category
    category_rel = relationship("category", back_populates="tasks")
    
    @property
    def category(self) -> str | None:
        """
        Devuelve el nombre de la categoría a partir de category_rel.
        Permite que el schema Pydantic acceda al nombre de la categoría.
        """
        return self.category_rel.name if self.category_rel else None
