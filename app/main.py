from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
import re
from pathlib import Path
from app.api.tasks_router import router as tasks_router
from app.api.ai_router import router as ai_router
from app.api.user_stories_router import router as user_stories_router
from app.core.config import get_settings

settings = get_settings()


class json_sanitizer_middleware:
    """
    Middleware ASGI que sanitiza el JSON antes de procesarlo.
    Convierte valores vacíos como "field": , a "field": null
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Solo aplicar sanitización a endpoints de IA (/ai/)
        path = scope.get("path", "")
        if not path.startswith("/ai/"):
            await self.app(scope, receive, send)
            return
        
        # Verificar si es un método que envía body
        method = scope.get("method", "")
        if method not in ["POST", "PUT", "PATCH"]:
            await self.app(scope, receive, send)
            return
        
        # Verificar content-type
        headers = dict(scope.get("headers", []))
        content_type = headers.get(b"content-type", b"").decode("utf-8", errors="ignore")
        if "application/json" not in content_type:
            await self.app(scope, receive, send)
            return
        
        # Acumular el body completo
        body_parts = []
        body_received = False
        
        async def receive_wrapper():
            nonlocal body_parts, body_received
            
            # Si ya procesamos el body, devolver mensaje vacío
            if body_received:
                return {"type": "http.request", "body": b"", "more_body": False}
            
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                body_parts.append(body)
                
                # Si es el último chunk, sanitizar
                if not message.get("more_body", False):
                    body_received = True
                    full_body = b"".join(body_parts)
                    body_str = full_body.decode("utf-8", errors="ignore")
                    
                    # Sanitizar JSON: convertir "field": , a "field": null
                    sanitized = re.sub(r':\s*,', ': null,', body_str)
                    sanitized = re.sub(r':\s*}', ': null}', sanitized)
                    
                    message = {
                        "type": "http.request",
                        "body": sanitized.encode("utf-8"),
                        "more_body": False
                    }
            return message
        
        await self.app(scope, receive_wrapper, send)


# Inicialización de la aplicación FastAPI principal
fastapi_app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	description=settings.app_description,
)

# Handler global para errores de validación: campos requeridos faltantes
@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	# Intentar leer el cuerpo enviado para identificar qué campos faltan
	try:
		payload = await request.json()
		if not isinstance(payload, dict):
			payload = {}
	except Exception:
		payload = {}

	# Nombre del parámetro del body en el endpoint de creación
	body_param = "task_input"
	body_data = payload if body_param not in payload else payload.get(body_param, {})
	if not isinstance(body_data, dict):
		body_data = {}

	# Campos requeridos según el modelo
	from app.models.task_model import task as TaskModel
	# Considerar todos los campos del modelo excepto 'id' como requeridos
	required_fields = [name for name in TaskModel.model_fields.keys() if name != "id"]

	missing_fields = [f for f in required_fields if f not in body_data]

	# Detectar errores específicos del campo effort_hours (no numérico / <= 0)
	invalid_msgs: list[str] = []
	for err in exc.errors():
		loc = err.get("loc", [])
		type_name = str(err.get("type", "")).lower()
		msg_text = str(err.get("msg", "")).lower()
		if isinstance(loc, (list, tuple)) and "effort_hours" in loc:
			if type_name == "greater_than" or "greater than" in msg_text:
				invalid_msgs.append("effort_hours debe ser mayor a 0")
			elif "valid number" in msg_text or "parsing" in type_name or "float" in type_name or "int" in type_name:
				invalid_msgs.append("effort_hours debe ser numérico")
		elif isinstance(loc, (list, tuple)) and "priority" in loc:
			# Mensaje claro para prioridad inválida
			from typing import get_args
			from app.models.task_model import task as TaskModel
			allowed = ", ".join(get_args(TaskModel.model_fields["priority"].annotation))
			invalid_msgs.append(f"priority debe ser uno de: {allowed}")
		elif isinstance(loc, (list, tuple)) and "status" in loc:
			# Mensaje claro para status inválido
			from typing import get_args
			from app.models.task_model import task as TaskModel
			allowed = ", ".join(get_args(TaskModel.model_fields["status"].annotation))
			invalid_msgs.append(f"status debe ser uno de: {allowed}")
		# Caso JSON inválido: intentar inferir errores de formato por valores sin comillas o vacíos
		elif type_name == "json_invalid":
			try:
				import re
				raw = (await request.body()).decode("utf-8", errors="ignore")
				
				# Detectar valores vacíos (ej: "field": , o "field": })
				all_fields = ["title", "description", "priority", "status", "assigned_to", 
				              "category", "risk_analysis", "risk_mitigation", "effort_hours"]
				for field in all_fields:
					# Patrón para detectar "field": , o "field": }
					pattern_empty = rf'"{field}"\s*:\s*[,}}]'
					if re.search(pattern_empty, raw):
						invalid_msgs.append(f"{field} tiene valor vacío o formato inválido")
				
				# Detectar valores string sin comillas para todos los campos string del esquema
				string_fields = ["title", "description", "priority", "status", "assigned_to", 
				                 "category", "risk_analysis", "risk_mitigation"]
				for field in string_fields:
					# Solo si no fue detectado como vacío
					if not any(field in m for m in invalid_msgs):
						m = re.search(rf'"{field}"\s*:\s*(.+)', raw)
						if m:
							after = m.group(1).lstrip()
							if after and not after.startswith('"') and not after.startswith(',') and not after.startswith('}'):
								invalid_msgs.append(f"{field} tiene formato inválido: debe ser texto entre comillas dobles")

				# Para effort_hours: solo marcar numérico cuando el token no está entre comillas y no es número
				if not any("effort_hours" in m for m in invalid_msgs):
					m_eh = re.search(r'"effort_hours"\s*:\s*([^,}\]\s]+)', raw)
					if m_eh:
						val = m_eh.group(1).strip()
						# Ignorar si comienza con comillas (no decidir aquí) 
						if val and not val.startswith('"'):
							# ¿Es numérico válido? (enteros/decimales con notación científica)
							is_numeric = re.fullmatch(r'-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?', val) is not None
							if not is_numeric:
								invalid_msgs.append("effort_hours debe ser numérico")
			except Exception:
				pass

	# Construir mensaje priorizando claridad para effort_hours numérico
	parts: list[str] = []
	if invalid_msgs:
		# Si detectamos errores de formato (json inválido) o numéricos de effort_hours, no mezclar con faltantes
		if any(m.startswith("effort_hours debe ser numérico") for m in invalid_msgs) or any("formato inválido" in m for m in invalid_msgs):
			parts.append("; ".join(invalid_msgs))
		else:
			if missing_fields:
				parts.append("Faltan los siguientes campos requeridos: " + ", ".join(missing_fields))
			parts.append("; ".join(invalid_msgs))
	elif missing_fields:
		parts.append("Faltan los siguientes campos requeridos: " + ", ".join(missing_fields))

	msg = " ".join(parts) if parts else "Datos incompletos o inválidos."

	return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"msg": msg, "detail": exc.errors()})

# Incluye el router principal para gestión de tareas (modular)
fastapi_app.include_router(tasks_router)

# Incluye el router de endpoints de IA
fastapi_app.include_router(ai_router)

# Incluye el router de historias de usuario (MVC con templates HTML)
fastapi_app.include_router(user_stories_router)

# Envolver FastAPI con el middleware de sanitización de JSON
app = json_sanitizer_middleware(fastapi_app)

__all__ = ["app"]



