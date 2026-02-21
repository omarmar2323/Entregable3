"""
Servicio CRUD para historias de usuario.
Maneja operaciones de base de datos para UserStory.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import user_story
from app.models.user_story_schema import user_story_create, user_story_update


class user_story_service:
    """
    Servicio para gestión de historias de usuario en base de datos.
    """

    @staticmethod
    def create_user_story(db: Session, user_story_data: user_story_create) -> user_story:
        """
        Crea una nueva historia de usuario en la base de datos.
        
        Args:
            db: Sesión de base de datos
            user_story_data: Datos de la historia a crear
            
        Returns:
            user_story: Instancia creada
        """
        db_user_story = user_story(**user_story_data.model_dump())
        db.add(db_user_story)
        db.commit()
        db.refresh(db_user_story)
        return db_user_story

    @staticmethod
    def get_user_story(db: Session, user_story_id: int) -> Optional[user_story]:
        """
        Obtiene una historia de usuario por ID.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia
            
        Returns:
            user_story o None si no existe
        """
        return db.query(user_story).filter(user_story.id == user_story_id).first()

    @staticmethod
    def get_all_user_stories(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[user_story]:
        """
        Obtiene todas las historias de usuario con paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            
        Returns:
            Lista de historias de usuario
        """
        return db.query(user_story).offset(skip).limit(limit).all()

    @staticmethod
    def update_user_story(
        db: Session,
        user_story_id: int,
        user_story_data: user_story_update
    ) -> Optional[user_story]:
        """
        Actualiza una historia de usuario existente.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia a actualizar
            user_story_data: Datos actualizados
            
        Returns:
            user_story actualizada o None si no existe
        """
        db_user_story = user_story_service.get_user_story(db, user_story_id)
        if not db_user_story:
            return None
        
        # Actualizar solo campos que no son None
        update_data = user_story_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user_story, field, value)
        
        db.commit()
        db.refresh(db_user_story)
        return db_user_story

    @staticmethod
    def delete_user_story(db: Session, user_story_id: int) -> bool:
        """
        Elimina una historia de usuario.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        db_user_story = user_story_service.get_user_story(db, user_story_id)
        if not db_user_story:
            return False
        
        db.delete(db_user_story)
        db.commit()
        return True

    @staticmethod
    def get_user_stories_by_project(db: Session, project_name: str) -> List[user_story]:
        """
        Obtiene historias de usuario filtradas por proyecto.
        
        Args:
            db: Sesión de base de datos
            project_name: Nombre del proyecto
            
        Returns:
            Lista de historias de usuario del proyecto
        """
        return db.query(user_story).filter(user_story.project == project_name).all()

    @staticmethod
    def update_user_story_role(db: Session, user_story_id: int, role: str) -> Optional[user_story]:
        """
        Actualiza el rol de una historia de usuario.
        Típicamente se usa para guardar la categoría determinada por IA.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia
            role: Nuevo valor del rol (categoría)
            
        Returns:
            user_story actualizada o None si no existe
        """
        db_user_story = user_story_service.get_user_story(db, user_story_id)
        if not db_user_story:
            return None
        
        db_user_story.role = role
        db.commit()
        db.refresh(db_user_story)
        return db_user_story

    @staticmethod
    def update_tasks_total_hours(db: Session, user_story_id: int) -> Optional[user_story]:
        """
        Actualiza el campo tasks_total_hours sumando las horas de todas las tareas asociadas.
        
        Args:
            db: Sesión de base de datos
            user_story_id: ID de la historia de usuario
            
        Returns:
            user_story actualizada o None si no existe
        """
        from app.database.models import task
        from sqlalchemy import func
        
        db_user_story = user_story_service.get_user_story(db, user_story_id)
        if not db_user_story:
            return None
        
        # Calcular suma total de horas de tareas asociadas usando SQL
        result = db.query(func.coalesce(func.sum(task.effort_hours), 0.0)).filter(
            task.user_story_id == user_story_id
        ).scalar()
        
        db_user_story.tasks_total_hours = float(result) if result else 0.0
        db.commit()
        db.refresh(db_user_story)
        return db_user_story