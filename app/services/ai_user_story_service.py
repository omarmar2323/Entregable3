"""
Servicio de IA para generar historias de usuario.
Usa Azure OpenAI para crear historias de usuario completas desde un prompt.
"""
import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import Optional
from openai import AzureOpenAI
from sqlalchemy.orm import Session
from app.models.user_story_schema import user_story_create
from app.database.models import category as category_model


class ai_user_story_service:
    """
    Servicio para generar historias de usuario con IA.
    """
    
    _settings: dict | None = None
    _client: AzureOpenAI | None = None
    
    @classmethod
    def _load_settings(cls) -> dict:
        """Carga la configuración del LLM desde llm_settings.json."""
        if cls._settings is None:
            settings_path = Path(__file__).resolve().parent.parent / "core" / "llm_settings.json"
            with settings_path.open("r", encoding="utf-8") as f:
                cls._settings = json.load(f)
        return cls._settings
    
    @classmethod
    def _get_client(cls) -> AzureOpenAI:
        """Obtiene o crea el cliente de Azure OpenAI."""
        if cls._client is None:
            settings = cls._load_settings()
            azure_config = settings["azure_openai"]
            cls._client = AzureOpenAI(
                azure_endpoint=azure_config["endpoint"],
                api_key=azure_config["api_key"],
                api_version="2024-02-15-preview"
            )
        return cls._client
    
    @classmethod
    def _get_model_params(cls) -> dict:
        """Obtiene los parámetros del modelo desde la configuración."""
        settings = cls._load_settings()
        return settings.get("model_parameters", {})
    
    @classmethod
    def _get_token_param_name(cls, model_name: str) -> str:
        """
        Detecta el nombre correcto del parámetro de tokens según el modelo.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            "max_completion_tokens" para gpt-5*, "max_tokens" para otros
        """
        if "gpt-5" in model_name.lower():
            return "max_completion_tokens"
        return "max_tokens"
    
    @classmethod
    def _is_parameter_supported(cls, model_name: str, param_name: str) -> bool:
        """
        Verifica si un parámetro es soportado por el modelo.
        gpt-5-nano solo soporta: model, messages, max_completion_tokens
        
        Args:
            model_name: Nombre del modelo
            param_name: Nombre del parámetro
            
        Returns:
            True si el parámetro es soportado
        """
        if "gpt-5" in model_name.lower():
            supported = {"temperature", "top_p", "frequency_penalty", "presence_penalty"}
            return param_name not in supported
        return True
    
    @classmethod
    def generate_user_story(cls, prompt: str, db: Optional[Session] = None) -> user_story_create:
        """
        Genera una historia de usuario completa a partir de un prompt.
        
        Args:
            prompt: Descripción o idea de la funcionalidad
            db: Sesión de base de datos para cargar categorías
            
        Returns:
            user_story_create: Historia de usuario generada
        """
        client = cls._get_client()
        params = cls._get_model_params()
        
        # Cargar categorías de la BD si hay sesión disponible
        categories_list = []
        categories_text = "Backend, Frontend, Testing, DevOps, Base de Datos"  # fallback
        if db:
            try:
                categories_db = db.query(category_model).all()
                if categories_db:
                    categories_list = [cat.name for cat in categories_db]
                    categories_text = ", ".join(categories_list)
            except Exception:
                pass
        
        system_prompt = f"""Eres un experto Product Owner y Scrum Master con amplia experiencia en desarrollo de software.
Tu tarea es convertir ideas y requisitos en historias de usuario completas y bien estructuradas.

Debes generar una historia de usuario en formato JSON con la siguiente estructura:
{{
    "project": "nombre del proyecto (inferido del contexto o genérico)",
    "role": "OBLIGATORIO: Selecciona UNA categoría de esta lista exacta: [{categories_text}]",
    "goal": "qué quiere lograr el usuario (máximo 500 caracteres)",
    "reason": "por qué es importante esta funcionalidad (máximo 500 caracteres)",
    "description": "descripción detallada de la historia de usuario, incluyendo criterios de aceptación",
    "priority": "baja, media, alta o bloqueante (según el contexto)",
    "story_points": "puntos de historia de 1 a 8 según complejidad",
    "effort_hours": "estimación de horas necesarias (número decimal)"
}}

REGLAS CRÍTICAS PARA EL CAMPO "role":
1. DEBES seleccionar EXACTAMENTE una de las categorías de la lista: [{categories_text}]
2. NO uses "usuario", "administrador", "cliente" ni roles genéricos
3. Analiza el prompt y selecciona la categoría técnica más apropiada
4. El valor de "role" debe coincidir EXACTAMENTE con una de las categorías listadas

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional, sin markdown, sin explicaciones."""

        user_prompt = f"Genera una historia de usuario completa basada en: {prompt}"
        
        model_name = params.get("modelo", "gpt-4")
        
        # Construir parámetros de forma condicional según el modelo
        request_params = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # Agregar token parameter con el nombre correcto
        token_param_name = cls._get_token_param_name(model_name)
        max_token_value = params.get("max_tokens", params.get("max_completion_tokens", 1000))
        request_params[token_param_name] = max_token_value
        
        # Agregar parámetros opcionales solo si el modelo los soporta
        optional_params = {
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.95),
            "frequency_penalty": params.get("frequency_penalty", 0.0),
            "presence_penalty": params.get("presence_penalty", 0.0)
        }
        
        for param_name, param_value in optional_params.items():
            if cls._is_parameter_supported(model_name, param_name):
                request_params[param_name] = param_value
        
        response = client.chat.completions.create(**request_params)
        
        content = response.choices[0].message.content.strip()
        
        # Limpiar markdown si existe
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Parsear respuesta JSON
        try:
            story_data = json.loads(content)
            # Validar que el role sea una categoría válida
            if categories_list and story_data.get("role") not in categories_list:
                # Limpiar el role si tiene palabras extra
                cleaned_role = cls._clean_category_name(story_data.get("role", ""), categories_list)
                story_data["role"] = cleaned_role
            return user_story_create(**story_data)
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: crear historia básica con categoría válida
            fallback_role = categories_list[0] if categories_list else "Backend"
            return user_story_create(
                project="Proyecto General",
                role=fallback_role,
                goal=prompt[:500] if len(prompt) <= 500 else prompt[:497] + "...",
                reason="Mejorar la experiencia del usuario y agregar funcionalidad solicitada",
                description=f"Historia de usuario generada desde: {prompt}",
                priority="media",
                story_points=3,
                effort_hours=8.0
            )
    
    @classmethod
    def generate_tasks_for_story(cls, user_story_data: dict, category: str, num_tasks: int = 4, existing_tasks: list = None) -> list:
        """
        Genera tareas para una historia de usuario de una categoría específica.
        
        Args:
            user_story_data: Diccionario con datos de la historia de usuario
            category: Categoría de las tareas a generar
            num_tasks: Número de tareas a generar
            existing_tasks: Lista opcional de tareas existentes para evitar duplicados
            
        Returns:
            list: Lista de diccionarios con datos de tareas
        """
        import re
        
        client = cls._get_client()
        params = cls._get_model_params()
        
        # Construir sección de tareas existentes para el prompt si las hay
        existing_tasks_section = ""
        if existing_tasks and len(existing_tasks) > 0:
            existing_tasks_section = "\n\nIMPORTANTE: Ya existen las siguientes tareas para esta historia. NO generes tareas similares o duplicadas:\n"
            for idx, task in enumerate(existing_tasks, 1):
                existing_tasks_section += f"{idx}. {task.get('title', 'Sin título')}: {task.get('description', '')[:100]}...\n"
            existing_tasks_section += "\nGenera tareas DIFERENTES y COMPLEMENTARIAS a las existentes."
        
        system_prompt = f"""Eres un experto Tech Lead especializado en {category}.
Tu tarea es descomponer una historia de usuario en tareas técnicas específicas y accionables, 
todas relacionadas con {category}.

Debes generar {num_tasks} tareas en formato JSON array con la siguiente estructura para cada tarea:
[
  {{
    "title": "título conciso de la tarea",
    "description": "descripción técnica detallada",
    "priority": "baja, media, alta o bloqueante",
    "effort_hours": 8.0,
    "status": "pendiente",
    "assigned_to": "rol sugerido",
    "category": "{category}"
  }}
]

Todas las tareas DEBEN ser de la categoría {category}.
Responde ÚNICAMENTE con un array JSON válido, sin markdown, sin explicaciones adicionales."""

        user_prompt = f"""Genera {num_tasks} tareas de {category} para implementar la siguiente historia de usuario:

Proyecto: {user_story_data.get('project', 'Proyecto General')}
Como: {user_story_data.get('role', 'usuario')}
Quiero: {user_story_data.get('goal', 'no especificado')}
Para: {user_story_data.get('reason', 'mejorar el sistema')}
Descripción: {user_story_data.get('description', 'sin descripción')}
Prioridad: {user_story_data.get('priority', 'media')}
Story Points: {user_story_data.get('story_points', 5)}

Todas las tareas deben ser de {category}.{existing_tasks_section}"""

        try:
            model_name = params.get("modelo", "gpt-4")
            
            request_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            token_param_name = cls._get_token_param_name(model_name)
            request_params[token_param_name] = 2500
            
            optional_params = {
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.95),
                "frequency_penalty": params.get("frequency_penalty", 0.0),
                "presence_penalty": params.get("presence_penalty", 0.0)
            }
            
            for param_name, param_value in optional_params.items():
                if cls._is_parameter_supported(model_name, param_name):
                    request_params[param_name] = param_value
            
            print(f"[DEBUG] Generando {num_tasks} tareas de {category}...")
            response = client.chat.completions.create(**request_params)
            
            content = response.choices[0].message.content.strip()
            print(f"[DEBUG] Respuesta recibida (primeros 300 chars):")
            print(f"[DEBUG] {content[:300]}")
            
            # Limpiar markdown
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            content = content.strip()
            
            # Buscar array JSON - usar regex greedy para capturar todo el array
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                content = json_match.group(0)
                print(f"[DEBUG] JSON extraído (primeros 500 chars): {content[:500]}")
            
            print(f"[DEBUG] Parseando JSON...")
            tasks_data = json.loads(content)
            
            # Validar que es una lista
            if not isinstance(tasks_data, list):
                print(f"[DEBUG] ⚠️  Respuesta no es array")
                if isinstance(tasks_data, dict):
                    if "tasks" in tasks_data:
                        tasks_data = tasks_data["tasks"]
                    else:
                        tasks_data = [tasks_data]
                else:
                    print(f"[DEBUG] ❌ No se puede convertir respuesta a lista")
                    return []
            
            print(f"[DEBUG] ✅ Se parsearon {len(tasks_data)} tareas de {category}")
            
            # Validar y limpiar cada tarea
            validated_tasks = []
            for idx, task in enumerate(tasks_data):
                if isinstance(task, dict):
                    if 'title' in task and 'assigned_to' in task:
                        # Asegurar que la categoría es la correcta
                        task['title'] = str(task.get('title', 'Tarea sin título'))[:200]
                        task['description'] = str(task.get('description', ''))
                        task['priority'] = task.get('priority', 'media')
                        task['effort_hours'] = cls._parse_effort_hours(task.get('effort_hours'))
                        task['status'] = task.get('status', 'pendiente')
                        task['assigned_to'] = str(task.get('assigned_to', 'equipo'))
                        task['category'] = category  # Forzar categoría correcta
                        
                        validated_tasks.append(task)
                        print(f"[DEBUG] Tarea {idx+1}: {task['title'][:40]}... ({category})")
            
            if not validated_tasks:
                print(f"[DEBUG] ⚠️  No hay tareas validadas")
                return []
            
            return validated_tasks
            
        except json.JSONDecodeError as json_err:
            print(f"[DEBUG] ❌ Error parsing JSON: {str(json_err)}")
            print(f"[DEBUG] Contenido problemático (primeros 500 chars):")
            print(f"[DEBUG] {content[:500]}")
            return []
        except Exception as e:
            print(f"[DEBUG] ❌ Error en generate_tasks_for_story: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @classmethod
    def _parse_effort_hours(cls, value) -> float:
        """Convierte el valor de effort_hours a float."""
        try:
            if value is None:
                return 8.0
            return float(value)
        except (TypeError, ValueError):
            return 8.0
    
    @classmethod
    def _clean_category_name(cls, raw_name: str, valid_categories: list) -> str:
        """
        Limpia y valida el nombre de categoría.
        Remueve palabras decorativas y valida contra la lista de categorías de la BD.
        
        Args:
            raw_name: Nombre crudo del LLM (puede ser "desarrollador backend")
            valid_categories: Lista de categorías válidas de la BD
            
        Returns:
            Nombre validado de la BD o fallback a primera categoría
        """
        if not raw_name:
            return valid_categories[0] if valid_categories else "Backend"
        
        clean_name = raw_name.strip()
        clean_name_lower = clean_name.lower()
        
        # 1. Búsqueda exacta (case-insensitive)
        for cat in valid_categories:
            if clean_name_lower == cat.lower():
                print(f"[DEBUG] _clean_category_name: '{raw_name}' → '{cat}' (coincidencia exacta)")
                return cat
        
        # 2. Si tiene palabras adicionales, intentar removerlas
        words_to_remove = [
            "desarrollador", "especialista", "experto", "ingeniero", "técnico",
            "tecnico", "arquitecto", "junior", "senior", "lead", "mid-level",
            "php", "python", "javascript", "java", "c#", "react", "angular",
            "vue", "node", "django", "flask", "docker", "kubernetes", "aws",
            "de ", "del ", "el ", "la ", "los ", "las ", "en ", "con ", "para "
        ]
        
        clean_name_temp = clean_name_lower
        for word in words_to_remove:
            clean_name_temp = clean_name_temp.replace(word.lower(), "").strip()
        
        # Buscar después de limpiar
        for cat in valid_categories:
            if clean_name_temp == cat.lower():
                print(f"[DEBUG] _clean_category_name: '{raw_name}' → '{cat}' (después de limpiar)")
                return cat
        
        # 3. Buscar si alguna categoría válida está DENTRO del nombre limpio
        for cat in valid_categories:
            if cat.lower() in clean_name_lower:
                print(f"[DEBUG] _clean_category_name: '{raw_name}' → '{cat}' (encontrada dentro)")
                return cat
        
        # 4. Fallback: primera categoría de la lista
        fallback = valid_categories[0] if valid_categories else "Backend"
        print(f"[DEBUG] _clean_category_name: '{raw_name}' → '{fallback}' (fallback)")
        return fallback
    
    @classmethod
    def _generate_fallback_tasks(cls, num_tasks: int = 6) -> list:
        """Genera tareas de demostración cuando la IA falla."""
        print(f"[DEBUG] Generando tareas fallback ({num_tasks})")
        
        fallback_templates = [
            {
                "title": "Configurar entorno de desarrollo",
                "description": "Instalar y configurar todas las dependencias necesarias para el proyecto",
                "priority": "alta",
                "effort_hours": 4.0,
                "status": "pendiente",
                "assigned_to": "devops",
                "category": "Infra"
            },
            {
                "title": "Diseñar base de datos",
                "description": "Crear diagrama ER y diseñar esquema de base de datos",
                "priority": "alta",
                "effort_hours": 8.0,
                "status": "pendiente",
                "assigned_to": "database_admin",
                "category": "Database"
            },
            {
                "title": "Implementar API REST",
                "description": "Crear endpoints principales del API",
                "priority": "alta",
                "effort_hours": 16.0,
                "status": "pendiente",
                "assigned_to": "backend_dev",
                "category": "Backend"
            },
            {
                "title": "Crear interfaz de usuario",
                "description": "Diseñar e implementar interfaz frontend",
                "priority": "media",
                "effort_hours": 12.0,
                "status": "pendiente",
                "assigned_to": "frontend_dev",
                "category": "Frontend"
            },
            {
                "title": "Crear tests automatizados",
                "description": "Escribir tests para API y lógica de negocio",
                "priority": "media",
                "effort_hours": 10.0,
                "status": "pendiente",
                "assigned_to": "qa_engineer",
                "category": "Testing"
            },
            {
                "title": "Documentar API",
                "description": "Crear documentación de endpoints y modelos de datos",
                "priority": "baja",
                "effort_hours": 6.0,
                "status": "pendiente",
                "assigned_to": "tech_writer",
                "category": "Documentation"
            }
        ]
        
        return fallback_templates[:num_tasks]
    
    @classmethod
    def determine_category_from_description(cls, user_story_data: dict, db) -> str:
        """
        Analiza la descripción de la historia de usuario para determinar 
        la categoría principal de trabajo.
        Obtiene el listado de categorías disponibles de la tabla categories
        y solicita respuesta JSON estructurada del LLM.
        
        Args:
            user_story_data: Diccionario con datos de la historia de usuario
            db: Sesión de base de datos SQLAlchemy
            
        Returns:
            str: Nombre de la categoría principal desde la BD
        """
        try:
            # Obtener todas las categorías de la BD
            from app.database.models import category
            categories_from_db = db.query(category).all()
            
            if not categories_from_db:
                print(f"[DEBUG] ⚠️  No hay categorías en la BD, usando 'Backend' por defecto")
                return "Backend"
            
            category_names = [cat.name for cat in categories_from_db]
            print(f"[DEBUG] Categorías disponibles en BD: {category_names}")
            print(f"[DEBUG] Total de categorías: {len(category_names)}")
            
        except Exception as db_error:
            print(f"[DEBUG] ⚠️  Error obteniendo categorías de BD: {str(db_error)}, usando 'Backend'")
            return "Backend"
        
        client = cls._get_client()
        params = cls._get_model_params()
        
        description = user_story_data.get('description', '')
        title = user_story_data.get('goal', '')
        
        # ============================================================
        # MAPEO DE PALABRAS CLAVE - TEMPLATES GENÉRICOS
        # Estos templates se mapean dinámicamente a las categorías reales de la BD
        # ============================================================
        keyword_mapping_templates = {
            "backend": {
                "keywords": ["servidor", "api", "endpoint", "lógica", "logica", "base de datos",
                            "consulta", "query", "php", "python", "java", "c#", "csharp", "node",
                            "express", "django", "flask", "spring", "autenticación", "autenticacion",
                            "sesión", "sesion", "desarrollador backend", "especialista server-side",
                            "lógica de negocio", "logica negocio", "procesar datos"]
            },
            "frontend": {
                "keywords": ["interfaz", "interfaz de usuario", "ui", "ux", "html", "css",
                            "javascript", "react", "angular", "vue", "typescript", "diseño",
                            "botón", "formulario", "form", "página web", "pagina web", "web",
                            "componentes", "estilos", "responsive", "desarrollador frontend",
                            "especialista frontend", "maquetación", "maquetacion", "visual"]
            },
            "database": {
                "keywords": ["base de datos", "base datos", "bd", "sql", "mysql", "postgresql",
                            "mongodb", "nosql", "esquema", "tablas", "tabla", "migración",
                            "migracion", "índices", "indices", "query", "consultas sql",
                            "modelo de datos", "datos", "almacenamiento"]
            },
            "testing": {
                "keywords": ["test", "prueba", "pruebas", "automatizado", "automatica", "qa",
                            "quality assurance", "casos de prueba", "junit", "pytest",
                            "mocha", "jasmine", "test unitario", "test e2e", "cobertura",
                            "tdd", "validación", "validacion"]
            },
            "devops": {
                "keywords": ["deploy", "deployment", "despliegue", "ci/cd", "cicd", "docker",
                            "kubernetes", "contenedor", "orquestación", "orquestacion",
                            "infraestructura", "infraestructura como código"]
            },
            "infrastructure": {
                "keywords": ["configuración", "configuracion", "servidor", "aws", "azure", "gcp",
                            "instalación", "instalacion", "setup", "ambiente", "entorno",
                            "linux", "windows", "red", "firewall"]
            },
            "documentation": {
                "keywords": ["documentación", "documentacion", "documento", "comentarios",
                            "wiki", "manual", "guía", "guia", "readme", "javadoc", "docstring",
                            "especificación", "especificacion", "api doc"]
            },
            "security": {
                "keywords": ["seguridad", "seguro", "encriptación", "encriptacion", "token",
                            "jwt", "oauth", "oauth2", "autenticación", "autenticacion",
                            "autorización", "autorizacion", "permisos", "roles", "acl",
                            "vulnerabilidad"]
            },
            "performance": {
                "keywords": ["performance", "rendimiento", "optimización", "optimizacion",
                            "caché", "cache", "velocidad", "rápido", "rapido", "latencia",
                            "memoria", "cpu", "escalabilidad", "escalable"]
            },
            "api": {
                "keywords": ["api", "endpoint", "rest", "graphql", "integración", "integracion",
                            "consumir", "servicio web", "soap", "rpc", "protocolo"]
            },
            "mobile": {
                "keywords": ["mobile", "móvil", "movil", "android", "ios", "iphone", "app",
                            "aplicación móvil", "aplicacion movil", "react native", "flutter"]
            },
            "architecture": {
                "keywords": ["arquitectura", "arquitectónico", "arquitectonico", "patrón",
                            "patron", "diseño de", "microservicios", "monolítico", "monolitico",
                            "estructura"]
            },
            "maintenance": {
                "keywords": ["mantenimiento", "bug", "fix", "corrección", "correccion",
                            "deuda técnica", "deuda tecnica", "limpieza de código"]
            },
            "bug fix": {
                "keywords": ["bug", "error", "fix", "corrección", "correccion", 
                            "parche", "problema", "issue", "defecto", "fallo"]
            },
            "feature": {
                "keywords": ["feature", "función", "funcionalidad", "nuevo", "nueva",
                            "capacidad", "requerimiento", "implementar"]
            },
            "refactoring": {
                "keywords": ["refactor", "refactorización", "refactorizacion", 
                            "limpieza", "mejora de código"]
            },
            "integration": {
                "keywords": ["integración", "integracion", "conectar", "conexión", 
                            "conexion", "api externa", "sincronización", "sincronizacion"]
            },
            "deployment": {
                "keywords": ["deploy", "despliegue", "deployment", "release", 
                            "producción", "produccion", "publicar", "subir"]
            },
            "monitoring": {
                "keywords": ["monitoring", "monitoreo", "monitorear", "logs", "log",
                            "alertas", "métricas", "metricas", "observabilidad",
                            "dashboard"]
            }
        }
        
        # ============================================================
        # MAPEO DINÁMICO: Categorías de la BD → Templates de palabras clave
        # ============================================================
        dynamic_keyword_mapping = {}
        
        for cat_obj in categories_from_db:
            cat_name = cat_obj.name
            cat_name_lower = cat_name.lower()
            
            # Buscar el template que mejor coincide con el nombre de la categoría
            best_match = None
            best_similarity = 0
            
            for template_key, template_data in keyword_mapping_templates.items():
                # Si el nombre de la categoría contiene el template_key o viceversa
                if template_key in cat_name_lower or (len(template_key) > 2 and template_key in cat_name_lower):
                    best_match = template_key
                    break
                # Búsqueda por similitud
                similarity = SequenceMatcher(None, template_key, cat_name_lower).ratio()
                if similarity > best_similarity and similarity > 0.4:
                    best_similarity = similarity
                    best_match = template_key
            
            # Si encontró un match, usar sus palabras clave
            if best_match:
                print(f"[DEBUG] Categoría '{cat_name}' mapeada a template '{best_match}'")
                dynamic_keyword_mapping[cat_name] = keyword_mapping_templates[best_match]["keywords"]
            else:
                print(f"[DEBUG] ⚠️  Categoría '{cat_name}' no tiene template, usando vacío")
                dynamic_keyword_mapping[cat_name] = []
        
        # Construir descripción de mapeos para el prompt (cargado de la BD)
        mapping_text = "MAPEO DE PALABRAS CLAVE → CATEGORÍA (CARGADO DE LA BD):\n"
        for cat, keywords in dynamic_keyword_mapping.items():
            if keywords:
                mapping_text += f"\n{cat}:\n"
                mapping_text += f"  • Palabras clave: {', '.join(keywords[:8])}...\n"
            else:
                mapping_text += f"\n{cat}: (Sin palabras clave específicas)\n"
        
        print(f"[DEBUG] Mapeo dinámico construido con {len(dynamic_keyword_mapping)} categorías")
        print(f"[DEBUG] Categorías mapeadas: {list(dynamic_keyword_mapping.keys())}")
        
        # Construir el listado de categorías dinámicamente para JSON
        categories_json_list = json.dumps(category_names, ensure_ascii=False, indent=2)
        
        system_prompt = f"""ERES UN CLASIFICADOR INTELIGENTE DE CATEGORÍAS DE SOFTWARE.
Tu tarea es analizar una historia de usuario y categorizar su trabajo en UNA de las categorías válidas.

CATEGORÍAS VÁLIDAS (ESTAS SON LAS ÚNICAS PERMITIDAS):
{categories_json_list}

{mapping_text}

INSTRUCCIONES CRÍTICAS:
1. DEBES responder ÚNICAMENTE en formato JSON: {{"categoria": "NombreExacto"}}
2. El valor "categoria" DEBE ser EXACTAMENTE uno de: {', '.join(category_names)}
3. NUNCA agregues palabras decorativas (desarrollador, especialista, ingeniero, etc.)
4. NUNCA incluyas lenguajes (PHP, Python, Java, React, Docker, etc.)
5. Lee las palabras clave de la descripción y mapea a la categoría correcta
6. Si la descripción tiene VARIAS palabras clave, elige la categoría MÁS DOMINANTE
7. SOLO RESPONDE CON JSON, nada más

DECISIÓN DE CATEGORÍA:
- Busca palabras clave en la descripción
- Encuentra todas las categorías que matches
- Elige la que tiene MÁS palabras clave coincidentes
- Si hay empate, elige la primera que se mencionó"""

        user_prompt = f"""ANALIZA ESTA HISTORIA Y CLASIFÍCALA

Título: {title}

Descripción: {description}

CATEGORÍAS DISPONIBLES:
{chr(10).join([f"  • {cat}" for cat in category_names])}

RESPONDE SOLO CON FORMATO JSON:
{{"categoria": "UnaDeEstasOpciones"}}

¿En cuál de estas categorías cae principalmente esta historia?"""

        try:
            model_name = params.get("modelo", "gpt-4")
            
            request_params = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.0,
                "max_tokens": 100
            }
            
            token_param_name = cls._get_token_param_name(model_name)
            request_params[token_param_name] = 100
            
            optional_params = {
                "temperature": 0.0,
                "top_p": params.get("top_p", 0.95),
            }
            
            for param_name, param_value in optional_params.items():
                if cls._is_parameter_supported(model_name, param_name):
                    request_params[param_name] = param_value
            
            print(f"[DEBUG] Determinando categoría principal de historia...")
            print(f"[DEBUG] Categorías disponibles: {category_names}")
            response = client.chat.completions.create(**request_params)
            
            response_text = response.choices[0].message.content.strip()
            print(f"[DEBUG] Respuesta del LLM (raw): '{response_text}'")
            
            # Parsear JSON
            category_response = None
            try:
                response_json = json.loads(response_text)
                category_response = response_json.get("categoria", "").strip()
                print(f"[DEBUG] Categoría extraída del JSON (raw): '{category_response}'")
                
                # LIMPIAR la categoría: remover palabras decorativas
                category_response = cls._clean_category_name(category_response, category_names)
                print(f"[DEBUG] Categoría después de limpiar: '{category_response}'")
                
            except json.JSONDecodeError as json_error:
                print(f"[DEBUG] ⚠️  Error parseando JSON: {str(json_error)}")
                print(f"[DEBUG] Intentando búsqueda de texto en: '{response_text}'")
                # Intentar extraer nombre de categoría del texto plano (búsqueda exacta primero)
                for cat in category_names:
                    if response_text == cat or f'"{cat}"' in response_text:
                        print(f"[DEBUG] ✅ Categoría encontrada (búsqueda exacta): {cat}")
                        return cat
                # Búsqueda parcial
                response_lower = response_text.lower()
                for cat in category_names:
                    if cat.lower() in response_lower:
                        print(f"[DEBUG] ✅ Categoría encontrada (búsqueda parcial): {cat}")
                        return cat
                category_response = None
            
            # Validar que la categoría esté EXACTAMENTE en el listado de la BD
            if category_response and category_response in category_names:
                print(f"[DEBUG] ✅ Categoría validada: {category_response}")
                return category_response
            else:
                print(f"[DEBUG] ❌ Categoría '{category_response}' NO en lista válida: {category_names}")
                
                # ÚLTIMO RECURSO: búsqueda por similitud (fuzzy matching)
                if category_response:
                    print(f"[DEBUG] Intentando búsqueda por similitud para '{category_response}'...")
                    best_match = None
                    best_score = 0.0
                    
                    for cat in category_names:
                        similarity = SequenceMatcher(None, category_response.lower(), cat.lower()).ratio()
                        print(f"[DEBUG]   Similitud con '{cat}': {similarity:.2f}")
                        if similarity > best_score:
                            best_score = similarity
                            best_match = cat
                    
                    if best_match and best_score > 0.5:
                        print(f"[DEBUG] ✅ Categoría encontrada por similitud: {best_match} (score: {best_score:.2f})")
                        return best_match
                
                # FALLBACK FINAL: usar la primera categoría
                fallback_cat = category_names[0] if category_names else "Backend"
                print(f"[DEBUG] ⚠️  Usando fallback: {fallback_cat}")
                return fallback_cat
                
        except Exception as e:
            print(f"[DEBUG] ❌ Error determinando categoría: {str(e)}")
            try:
                fallback_cat = category_names[0] if category_names else "Backend"
                print(f"[DEBUG] ⚠️  Exception - usando fallback: {fallback_cat}")
                return fallback_cat
            except:
                return "Backend"
