from typing import Literal, Annotated, Optional, Any
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, field_validator


# Categorías disponibles para las tareas
task_category = Literal[
    "Frontend",
    "Backend", 
    "Testing",
    "Infra",
    "DevOps",
    "Database",
    "Security",
    "API",
    "UI_UX",
    "Documentation",
    "Architecture",
    "Mobile",
    "Cloud",
    "Analytics"
]


class task(BaseModel):
    """
    Modelo que representa una tarea en el sistema.

    Atributos:
        id (int | None): ID autoincremental de la tarea (se asigna automáticamente al crearla).
        title (str): Título breve que resume la tarea.
        description (str): Descripción detallada de la tarea.
        priority (str): Prioridad de la tarea. Solo permite: 'baja', 'media', 'alta', 'bloqueante'.
        effort_hours (float): Estimación de esfuerzo en horas para resolver la tarea.
        status (str): Estado de la tarea. Solo permite: 'pendiente', 'en_progreso', 'en_revision', 'completada'.
        assigned_to (str): Persona a la que está asignada la tarea.
        category (str | None): Categoría de la tarea (Frontend, Backend, Testing, etc.).
        risk_analysis (str | None): Análisis de riesgos de la tarea.
        risk_mitigation (str | None): Plan de mitigación de riesgos.

    Métodos:
        to_dict(): Devuelve un diccionario con los datos de la tarea.
        from_dict(data): Crea una instancia de `task` a partir de un diccionario.
    """
    # Ejemplo para Swagger/OpenAPI (aparece precargado en /docs)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "tarea_de_ejemplo",
                "description": "descripcion_de_la_tarea",
                "priority": "alta",
                "effort_hours": 4.5,
                "status": "pendiente",
                "assigned_to": "juan_perez",
                "category": "Backend",
                "risk_analysis": "analisis_de_riesgos",
                "risk_mitigation": "plan_de_mitigacion"
            }
        }
    )
    id: int | None = None
    title: str
    description: str = ""
    priority: Literal["baja", "media", "alta", "bloqueante"]
    effort_hours: Optional[Annotated[StrictFloat, Field(gt=0)]] = None
    status: Literal["pendiente", "en_progreso", "en_revision", "completada"]
    assigned_to: str
    category: Optional[task_category] = None
    risk_analysis: Optional[str] = None
    risk_mitigation: Optional[str] = None

    @field_validator("category", "risk_analysis", "risk_mitigation", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte strings vacíos a None para campos opcionales."""
        if v == "":
            return None
        return v

    def to_dict(self) -> dict:
        """Devuelve un diccionario serializable con los datos de la tarea."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "task":
        """Crea una tarea a partir de un diccionario de datos."""
        return cls(**data)


class task_ai_input(BaseModel):
    """
    Modelo permisivo para endpoints de IA.
    
    Acepta cualquier valor en effort_hours y lo convierte a None si es inválido,
    permitiendo que la IA genere el valor.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "tarea_de_ejemplo",
                "description": "descripcion_de_la_tarea",
                "priority": "alta",
                "effort_hours": None,
                "status": "pendiente",
                "assigned_to": "juan_perez",
                "category": "Backend",
                "risk_analysis": "",
                "risk_mitigation": ""
            }
        }
    )
    id: int | None = None
    title: str
    description: str = ""
    priority: Literal["baja", "media", "alta", "bloqueante"]
    effort_hours: Optional[Any] = None  # Acepta cualquier valor
    status: Literal["pendiente", "en_progreso", "en_revision", "completada"]
    assigned_to: str
    category: Optional[str] = None  # Más permisivo para categorías
    risk_analysis: Optional[str] = None
    risk_mitigation: Optional[str] = None

    @field_validator("category", "risk_analysis", "risk_mitigation", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convierte strings vacíos a None para campos opcionales."""
        if v == "":
            return None
        return v

    @field_validator("effort_hours", mode="before")
    @classmethod
    def normalize_effort_hours(cls, v):
        """Convierte effort_hours inválido a None para que la IA lo genere."""
        if v == "" or v is None:
            return None
        if isinstance(v, (int, float)) and v <= 0:
            return None
        # Si es un número válido > 0, mantenerlo
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
        # Cualquier otro valor inválido -> None
        return None

    def to_task(self) -> task:
        """Convierte a modelo task estándar."""
        return task(
            id=self.id,
            title=self.title,
            description=self.description,
            priority=self.priority,
            effort_hours=self.effort_hours if isinstance(self.effort_hours, float) and self.effort_hours > 0 else None,
            status=self.status,
            assigned_to=self.assigned_to,
            category=self.category if self.category in task_category.__args__ else None,
            risk_analysis=self.risk_analysis,
            risk_mitigation=self.risk_mitigation
        )



