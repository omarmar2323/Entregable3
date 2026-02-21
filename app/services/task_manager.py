import json
from pathlib import Path
from typing import List

from app.models.task_model import task
from pydantic import ValidationError


class task_manager:
    """
    Clase utilitaria para la gestión de tareas usando un archivo JSON de respaldo.

    El archivo de datos se encuentra en 'data/tasks_json.json', con el siguiente formato:
    {
        "Tasks": [ ... ],      # Lista de tareas serializadas
        "last_id": 5           # Último ID asignado
    }

    Métodos estáticos:
        - load_tasks(): Carga la lista de tareas actuales desde el JSON.
        - save_tasks(tasks): Guarda la lista actual de tareas en el JSON.
        - create_task(new_task): Inserta una nueva tarea, asignando un ID único.
        - get_all_tasks(): Lista todas las tareas almacenadas.
        - get_task_by_id(task_id): Busca una tarea por su ID.
        - update_task(task_id, updated_task): Reemplaza los datos de una tarea existente.
        - delete_task(task_id): Elimina una tarea por su ID.
    """

    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_file: Path = base_dir / "data" / "tasks_json.json"
    tasks_key: str = "Tasks"
    last_id_key: str = "last_id"

    @staticmethod
    def _ensure_data_file_exists() -> None:
        """
        Garantiza que el archivo y carpeta de datos existen. Si no, los crea con estructura vacía.
        """
        task_manager.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not task_manager.data_file.exists():
            initial_content = {
                task_manager.tasks_key: [],
                task_manager.last_id_key: 0,
            }
            with task_manager.data_file.open("w", encoding="utf-8") as file:
                json.dump(initial_content, file, ensure_ascii=False, indent=2)

    @staticmethod
    def load_tasks() -> List[task]:
        """
        Carga todas las tareas del archivo JSON y las convierte en objetos task.
        Returns:
            List[task]: Lista de tareas.
        """
        task_manager._ensure_data_file_exists()
        try:
            with task_manager.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            # Recuperar de JSON corrupto: restablecer estructura vacía para evitar 500
            data = {task_manager.tasks_key: [], task_manager.last_id_key: 0}
            with task_manager.data_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        tasks_data = data.get(task_manager.tasks_key, [])
        if not isinstance(tasks_data, list):
            tasks_data = []
        valid_tasks: List[task] = []
        for t in tasks_data:
            try:
                valid_tasks.append(task.from_dict(t))
            except ValidationError:
                # Omitir entradas inválidas (por ejemplo, effort_hours <= 0)
                continue
        return valid_tasks

    @staticmethod
    def save_tasks(tasks: List[task]) -> None:
        """
        Guarda la lista de tareas en el archivo JSON, manteniendo el último ID usado.
        Args:
            tasks (List[task]): Lista de tareas a guardar.
        """
        task_manager._ensure_data_file_exists()
        # Cargar de forma segura; si el JSON está corrupto, reconstruir estructura base
        try:
            with task_manager.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {task_manager.tasks_key: [], task_manager.last_id_key: 0}
        # Asegurar clave de tareas como lista
        if not isinstance(data.get(task_manager.tasks_key), list):
            data[task_manager.tasks_key] = []
        data[task_manager.tasks_key] = [t.to_dict() for t in tasks]
        with task_manager.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    @staticmethod
    def _get_next_id() -> int:
        """
        Obtiene el siguiente ID disponible y lo incrementa en el JSON.
        Returns:
            int: Nuevo ID único.
        """
        task_manager._ensure_data_file_exists()
        # Leer de forma segura; si corrupto, reiniciar estructura
        try:
            with task_manager.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {task_manager.tasks_key: [], task_manager.last_id_key: 0}
        # Normalizar last_id
        try:
            last_id_raw = data.get(task_manager.last_id_key, 0)
            last_id = int(last_id_raw) if isinstance(last_id_raw, (int, float, str)) else 0
            if last_id < 0:
                last_id = 0
        except Exception:
            last_id = 0
        next_id = last_id + 1
        data[task_manager.last_id_key] = next_id
        # Garantizar que la clave de tareas exista como lista para no perder datos
        if not isinstance(data.get(task_manager.tasks_key), list):
            data[task_manager.tasks_key] = []
        with task_manager.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        return next_id

    @staticmethod
    def create_task(new_task: task) -> task:
        """
        Crea e inserta una nueva tarea, asignándole el siguiente ID autoincremental.
        Args:
            new_task (task): Datos de la tarea (sin id).
        Returns:
            task: Tarea creada (ya con id).
        """
        tasks = task_manager.load_tasks()
        new_id = task_manager._get_next_id()
        new_task.id = new_id
        tasks.append(new_task)
        task_manager.save_tasks(tasks)
        return new_task

    @staticmethod
    def get_all_tasks() -> List[task]:
        """Devuelve la lista completa de tareas."""
        return task_manager.load_tasks()

    @staticmethod
    def get_task_by_id(task_id: int) -> task | None:
        """
        Busca una tarea por id.
        Returns:
            task (si existe), None (si no existe)
        """
        tasks = task_manager.load_tasks()
        for existing_task in tasks:
            if existing_task.id == task_id:
                return existing_task
        return None

    @staticmethod
    def update_task(task_id: int, updated_task: task) -> task | None:
        """
        Actualiza una tarea por id.
        Args:
            task_id (int): ID de la tarea a actualizar.
            updated_task (task): Datos nuevos (id será reemplazado por el original).
        Returns:
            task: La tarea actualizada, o None si no se encontró.
        """
        tasks = task_manager.load_tasks()
        for index, existing_task in enumerate(tasks):
            if existing_task.id == task_id:
                updated_task.id = task_id
                tasks[index] = updated_task
                task_manager.save_tasks(tasks)
                return updated_task
        return None

    @staticmethod
    def delete_task(task_id: int) -> bool:
        """
        Elimina una tarea por ID.
        Returns:
            True si la tarea fue eliminada, False si no se encontró.
        """
        tasks = task_manager.load_tasks()
        filtered_tasks = [t for t in tasks if t.id != task_id]
        if len(filtered_tasks) == len(tasks):
            return False
        task_manager.save_tasks(filtered_tasks)
        return True



