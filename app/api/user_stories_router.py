"""
Router para historias de usuario.
Maneja endpoints MVC con templates HTML usando Jinja2.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.database import get_db
from app.services.user_story_service import user_story_service
from app.services.ai_user_story_service import ai_user_story_service
from app.services.task_service import task_service
from app.services.llm_service import llm_service
from app.models.user_story_schema import user_story_create
from app.models.task_schema import task_create
from app.models.task_model import task, task_category


# Categorías válidas para el modelo Pydantic
VALID_CATEGORIES = ["Frontend", "Backend", "Testing", "Infra", "DevOps", "Database", 
                    "Security", "API", "UI_UX", "Documentation", "Architecture", 
                    "Mobile", "Cloud", "Analytics"]

# Mapeo de categorías de BD a categorías del modelo
CATEGORY_MAPPING = {
    "ui/ux": "UI_UX",
    "ui_ux": "UI_UX",
    "uiux": "UI_UX",
    "ux/ui": "UI_UX",
    "ux": "UI_UX",
    "ui": "UI_UX",
    "front-end": "Frontend",
    "front end": "Frontend",
    "back-end": "Backend",
    "back end": "Backend",
    "qa": "Testing",
    "test": "Testing",
    "infrastructure": "Infra",
    "infraestructura": "Infra",
    "db": "Database",
    "base de datos": "Database",
    "docs": "Documentation",
    "documentacion": "Documentation",
    "documentación": "Documentation",
    "arch": "Architecture",
    "arquitectura": "Architecture",
    "seguridad": "Security",
    "movil": "Mobile",
    "móvil": "Mobile",
    "nube": "Cloud",
    "analítica": "Analytics",
    "analitica": "Analytics",
}


def normalize_category(category: str) -> str:
    """
    Normaliza el nombre de categoría para que coincida con task_category Literal.
    
    Args:
        category: Nombre de categoría (puede venir de BD o LLM)
        
    Returns:
        Nombre de categoría válido para Pydantic
    """
    if not category:
        return "Backend"
    
    # Si ya es válida, devolverla con capitalización correcta
    for valid in VALID_CATEGORIES:
        if category.lower() == valid.lower():
            return valid
    
    # Buscar en el mapeo
    category_lower = category.lower().strip()
    if category_lower in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[category_lower]
    
    # Fallback: Backend
    print(f"[DEBUG] Categoría '{category}' no reconocida, usando 'Backend'")
    return "Backend"


router = APIRouter(prefix="/user-stories", tags=["user_stories"])

# Configurar templates
templates_path = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))


@router.get("", response_class=HTMLResponse)
async def get_user_stories_page(request: Request, db: Session = Depends(get_db)):
    """
    GET /user-stories
    Muestra la página HTML con todas las historias de usuario.
    Incluye un formulario para generar nuevas historias con IA.
    """
    user_stories = user_story_service.get_all_user_stories(db)
    return templates.TemplateResponse(
        "user_stories.html",
        {
            "request": request,
            "user_stories": user_stories
        }
    )


@router.post("")
async def create_user_story_from_prompt(
    prompt: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    POST /user-stories
    Recibe un prompt desde el formulario, genera una historia de usuario con IA
    y la almacena en base de datos.
    """
    try:
        # Generar historia de usuario con IA (pasando db para cargar categorías)
        user_story_data = ai_user_story_service.generate_user_story(prompt, db)
        
        # Guardar en base de datos
        created_story = user_story_service.create_user_story(db, user_story_data)
        
        # Redireccionar a la página de historias
        return RedirectResponse(url="/user-stories", status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar historia: {str(e)}")


@router.post("/{user_story_id}/generate-tasks")
async def generate_tasks_for_user_story(
    user_story_id: int,
    db: Session = Depends(get_db)
):
    """
    POST /user-stories/{id}/generate-tasks
    Genera tareas automáticamente para una historia de usuario usando IA.
    
    Flujo:
    1. Obtener historia de usuario de la BD
    2. Analizar description para determinar categoría principal
    3. Generar tareas de esa categoría especifica
    4. Para cada tarea, mejora usando endpoints de IA:
       - Descripción detallada
       - Estimación de esfuerzo
       - Análisis de riesgos
    5. Almacena en base de datos
    6. Redirige a página de tareas
    """
    # Verificar que la historia existe
    user_story = user_story_service.get_user_story(db, user_story_id)
    if not user_story:
        raise HTTPException(status_code=404, detail="Historia de usuario no encontrada")
    
    try:
        # Convertir a diccionario para pasarlo al servicio de IA
        story_dict = {
            "project": user_story.project,
            "role": user_story.role,
            "goal": user_story.goal,
            "reason": user_story.reason,
            "description": user_story.description,
            "priority": user_story.priority.value if hasattr(user_story.priority, 'value') else user_story.priority,
            "story_points": user_story.story_points
        }
        
        # 1. Determinar la categoría principal basada en la descripción
        print(f"[DEBUG] Determinando categoría para historia {user_story_id}...")
        raw_category = ai_user_story_service.determine_category_from_description(story_dict, db)
        print(f"[DEBUG] Categoría determinada (raw): {raw_category}")
        
        # Normalizar categoría para que sea válida en Pydantic
        category = normalize_category(raw_category)
        print(f"[DEBUG] Categoría normalizada: {category}")
        
        # NOTA: El rol de la historia de usuario NO se modifica.
        # La categoría se usa solo para generar tareas de ese tipo.
        
        # 2. Verificar si ya existen tareas para esta historia
        existing_tasks = task_service.get_tasks_by_user_story(db, user_story_id)
        existing_tasks_info = []
        
        if existing_tasks:
            # Si ya hay tareas, generar solo 1 tarea nueva
            num_tasks_to_generate = 1
            # Preparar info de tareas existentes para el prompt
            existing_tasks_info = [
                {"title": t.title, "description": t.description[:200] if t.description else ""}
                for t in existing_tasks
            ]
            print(f"[DEBUG] Historia ya tiene {len(existing_tasks)} tareas. Generando solo 1 nueva tarea.")
        else:
            # Si no hay tareas, comportamiento normal (4 tareas)
            num_tasks_to_generate = 4
            print(f"[DEBUG] Historia sin tareas previas. Generando {num_tasks_to_generate} tareas.")
        
        # 3. Generar tareas de esa categoría específica
        print(f"[DEBUG] Generando {num_tasks_to_generate} tareas de {category}...")
        tasks_data = ai_user_story_service.generate_tasks_for_story(
            story_dict, 
            category=category, 
            num_tasks=num_tasks_to_generate,
            existing_tasks=existing_tasks_info
        )
        print(f"[DEBUG] Tareas generadas: {len(tasks_data)} - Tipo: {type(tasks_data)}")
        
        if not tasks_data:
            raise HTTPException(
                status_code=500, 
                detail=f"La IA no generó tareas de {category}. Intenta de nuevo."
            )
        
        print(f"[DEBUG] Contenido tareas_data: {tasks_data}")
        
        created_tasks_count = 0
        errors = []
        
        # 3. Procesar cada tarea generada para mejorarla usando los servicios de IA
        for idx, task_dict in enumerate(tasks_data):
            try:
                print(f"[DEBUG] Procesando tarea {idx+1}/{len(tasks_data)}: {task_dict.get('title', 'Sin título')}")
                
                # Crear objeto task temporal para procesamiento con IA
                temp_task = task(
                    title=task_dict.get("title", "Tarea sin título"),
                    description=task_dict.get("description", ""),
                    priority=task_dict.get("priority", "media"),
                    effort_hours=task_dict.get("effort_hours"),
                    status=task_dict.get("status", "pendiente"),
                    assigned_to=task_dict.get("assigned_to", "equipo_desarrollo"),
                    category=category,  # Usar categoría determinada
                    risk_analysis=None,
                    risk_mitigation=None
                )
                
                print(f"[DEBUG]   - Antes: categoría={temp_task.category}, horas={temp_task.effort_hours}")
                
                # 1. Mejorar descripción si está vacía o es muy corta
                if not temp_task.description or len(temp_task.description) < 50:
                    print(f"[DEBUG]   - Generando descripción...")
                    temp_task = llm_service.generate_description(temp_task)
                
                # 2. NO categorizar (ya está determinada por la historia)
                print(f"[DEBUG]   - Categoría fija: {category}")
                
                # 3. Estimar esfuerzo
                print(f"[DEBUG]   - Estimando esfuerzo...")
                temp_task = llm_service.estimate_effort(temp_task)
                
                # 4. Auditar riesgos
                print(f"[DEBUG]   - Auditando riesgos...")
                temp_task = llm_service.audit_task(temp_task)
                
                print(f"[DEBUG]   - Después: categoría={temp_task.category}, horas={temp_task.effort_hours}")
                
                # Preparar datos para guardar en BD
                task_dict_to_save = {
                    "title": temp_task.title,
                    "description": temp_task.description,
                    "priority": temp_task.priority,
                    "effort_hours": temp_task.effort_hours,
                    "status": temp_task.status,
                    "assigned_to": temp_task.assigned_to,
                    "category": category,  # Usar categoría determinada
                    "risk_analysis": temp_task.risk_analysis,
                    "risk_mitigation": temp_task.risk_mitigation,
                    "user_story_id": user_story_id
                }
                
                # Crear objeto task_create y guardar en BD
                task_obj = task_create(**task_dict_to_save)
                saved_task = task_service.create_task(db, task_obj)
                
                print(f"[DEBUG]   ✅ Tarea guardada en BD con ID: {saved_task.id}")
                
                created_tasks_count += 1
                
            except Exception as task_error:
                # Continuar con la siguiente tarea si una falla
                error_msg = f"Error en tarea {idx+1}: {str(task_error)}"
                print(f"[DEBUG]   ❌ {error_msg}")
                errors.append(error_msg)
                continue
        
        print(f"[DEBUG] Total tareas creadas: {created_tasks_count}")
        print(f"[DEBUG] Todas de categoría: {category}")
        
        # Validar que se crearon las tareas esperadas
        # Si ya había tareas, esperamos al menos 1; si no, esperamos al menos 2
        min_required = 1 if existing_tasks else 2
        if created_tasks_count < min_required:
            error_detail = f"No se generaron suficientes tareas. Se crearon {created_tasks_count} de {min_required} requeridas."
            if errors:
                error_detail += f" Errores: {'; '.join(errors[:3])}"
            raise HTTPException(
                status_code=500, 
                detail=error_detail
            )
        
        # Actualizar el total de horas de tareas en la historia de usuario
        user_story_service.update_tasks_total_hours(db, user_story_id)
        print(f"[DEBUG] ✅ tasks_total_hours actualizado para historia {user_story_id}")
        
        # Redireccionar a la página de tareas
        return RedirectResponse(
            url=f"/user-stories/{user_story_id}/tasks",
            status_code=303
        )
    
    except HTTPException:
        # Re-lanzar excepciones HTTP
        raise
    except Exception as e:
        error_msg = f"Error al generar tareas: {str(e)}"
        print(f"[DEBUG] ❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{user_story_id}/tasks", response_class=HTMLResponse)
async def get_user_story_tasks_page(
    user_story_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    GET /user-stories/{id}/tasks
    Muestra la página HTML con las tareas de una historia de usuario específica.
    """
    # Verificar que la historia existe
    user_story = user_story_service.get_user_story(db, user_story_id)
    if not user_story:
        raise HTTPException(status_code=404, detail="Historia de usuario no encontrada")
    
    # Obtener tareas asociadas
    tasks = task_service.get_tasks_by_user_story(db, user_story_id)
    
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "user_story": user_story,
            "tasks": tasks
        }
    )
