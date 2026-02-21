"""
Servicio CRUD para tareas.
Maneja operaciones de base de datos para Task.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import task, category
from app.models.task_schema import task_create, task_update


class task_service:
    """
    Servicio para gestión de tareas en base de datos.
    """

    @staticmethod
    def _get_category_id(db: Session, category_name: Optional[str]) -> Optional[int]:
        """
        Resuelve un nombre de categoría a su ID.
        Soporta variantes como UI_UX → UI/UX.
        
        Args:
            db: Sesión de base de datos
            category_name: Nombre de la categoría
            
        Returns:
            ID de la categoría o None si no existe
        """
        if not category_name:
            return None
        
        # Búsqueda exacta primero
        cat = db.query(category).filter(category.name == category_name).first()
        if cat:
            return cat.id
        
        # Mapeo de variantes normalizadas a nombres en BD
        variant_mapping = {
            "UI_UX": ["UI/UX", "UX/UI", "UI-UX", "UX-UI"],
            "UI/UX": ["UI_UX", "UX_UI", "UI-UX", "UX-UI"],
        }
        
        # Intentar con variantes
        if category_name in variant_mapping:
            for variant in variant_mapping[category_name]:
                cat = db.query(category).filter(category.name == variant).first()
                if cat:
                    return cat.id
        
        # Búsqueda case-insensitive como último recurso
        cat = db.query(category).filter(
            category.name.ilike(category_name)
        ).first()
        return cat.id if cat else None

    @staticmethod
    def create_task(db: Session, task_data: task_create) -> task:
        """
        Crea una nueva tarea en la base de datos.
        Resuelve el nombre de categoría a su ID.
        
        Args:
            db: Sesión de base de datos
            task_data: Datos de la tarea a crear
            
        Returns:
            task: Instancia creada
        """
        data = task_data.model_dump()
        
        # Resolver category name a category_id
        category_name = data.pop("category", None)
        if category_name:
            data["category_id"] = task_service._get_category_id(db, category_name)
        
        db_task = task(**data)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[task]:
        """
        Obtiene una tarea por ID.
        
        Args:
            db: Sesión de base de datos
            task_id: ID de la tarea
            
        Returns:
            task o None si no existe
        """
        return db.query(task).filter(task.id == task_id).first()

    @staticmethod
    def get_all_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[task]:
        """
        Obtiene todas las tareas con paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de tareas
        """
        return db.query(task).offset(skip).limit(limit).all()

    @staticmethod
    def get_tasks_by_user_story(
        db: Session,
        user_story_id: int
    ) -> List[task]:
        """
        Obtiene todas las tareas asociadas a una historia de usuario.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia de usuario
            
        Returns:
            Lista de tareas
        """
        return db.query(task).filter(task.user_story_id == user_story_id).all()

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_data: task_update
    ) -> Optional[task]:
        """
        Actualiza una tarea existente.
        Resuelve el nombre de categoría a su ID si se proporciona.
        
        Args:
            db: Sesión de base de datos
            task_id: ID de la tarea a actualizar
            task_data: Datos actualizados
            
        Returns:
            task actualizada o None si no existe
        """
        db_task = task_service.get_task(db, task_id)
        if not db_task:
            return None
        
        # Actualizar solo campos que no son None
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Resolver category name a category_id si se proporciona
        if "category" in update_data:
            category_name = update_data.pop("category", None)
            if category_name:
                update_data["category_id"] = task_service._get_category_id(db, category_name)
        
        # Aplicar los cambios a la tarea
        for key, value in update_data.items():
            setattr(db_task, key, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """
        Elimina una tarea.
        
        Args:
            db: Sesión de base de datos
            task_id: ID de la tarea a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        db_task = task_service.get_task(db, task_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True

    @staticmethod
    def get_tasks_by_status(db: Session, status: str) -> List[task]:
        """
        Obtiene tareas filtradas por estado.
        
        Args:
            db: Sesión de base de datos
            status: Estado de las tareas
            
        Returns:
            Lista de tareas con el estado especificado
        """
        return db.query(task).filter(task.status == status).all()

    @staticmethod
    def get_tasks_by_assigned(db: Session, assigned_to: str) -> List[task]:
        """
        Obtiene tareas asignadas a una persona específica.
        
        Args:
            db: Sesión de base de datos
            assigned_to: Nombre de la persona
            
        Returns:
            Lista de tareas asignadas
        """
        return db.query(task).filter(task.assigned_to == assigned_to).all()
