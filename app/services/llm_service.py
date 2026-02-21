"""
Servicio para interactuar con Azure OpenAI LLM.

Este módulo proporciona funciones para generar descripciones, categorizar tareas,
estimar esfuerzo y realizar análisis de riesgos usando Azure OpenAI.
"""

import json
import re
from pathlib import Path
from typing import Optional

from openai import AzureOpenAI

from app.models.task_model import task, task_category


class llm_service:
    """
    Servicio para interacciones con Azure OpenAI LLM.
    
    Carga la configuración desde llm_settings.json y proporciona métodos
    para las diferentes operaciones de IA sobre tareas.
    """
    
    _settings: dict | None = None
    _client: AzureOpenAI | None = None
    _categories: list | None = None
    
    @classmethod
    def _load_settings(cls) -> dict:
        """
        Carga la configuración del LLM desde el archivo llm_settings.json.
        
        Returns:
            dict: Configuración del LLM.
        """
        if cls._settings is None:
            settings_path = Path(__file__).resolve().parent.parent / "core" / "llm_settings.json"
            with settings_path.open("r", encoding="utf-8") as f:
                cls._settings = json.load(f)
        return cls._settings
    
    @classmethod
    def _load_categories(cls) -> list:
        """
        Carga las categorías desde la base de datos.
        
        Returns:
            list: Lista de categorías disponibles.
        """
        if cls._categories is None:
            from app.database.database import session_local
            from app.database.models import category
            
            session = session_local()
            try:
                categories = session.query(category).all()
                cls._categories = [cat.name for cat in categories]
            finally:
                session.close()
        
        return cls._categories
    
    @classmethod
    def _get_client(cls) -> AzureOpenAI:
        """
        Obtiene o crea el cliente de Azure OpenAI.
        
        Returns:
            AzureOpenAI: Cliente configurado.
        """
        if cls._client is None:
            settings = cls._load_settings()
            azure_config = settings["azure_openai"]
            cls._client = AzureOpenAI(
                azure_endpoint=azure_config["endpoint"],
                api_key=azure_config["api_key"],
                api_version="2025-01-01-preview"
            )
        return cls._client
    
    @classmethod
    def _get_model_params(cls) -> dict:
        """
        Obtiene los parámetros del modelo desde la configuración.
        
        Returns:
            dict: Parámetros del modelo (temperature, max_tokens, etc.).
        """
        settings = cls._load_settings()
        return settings.get("model_parameters", {})
    
    @classmethod
    def _get_token_param_name(cls, model_name: str) -> str:
        """
        Determina el nombre del parámetro para tokens según el modelo.
        
        Modelos gpt-5 y posteriores usan 'max_completion_tokens'.
        Modelos anteriores usan 'max_tokens'.
        
        Args:
            model_name: Nombre del modelo de IA.
            
        Returns:
            str: Nombre del parámetro ('max_completion_tokens' o 'max_tokens').
        """
        if "gpt-5" in model_name or "gpt-4o" in model_name:
            return "max_completion_tokens"
        return "max_tokens"
    
    @classmethod
    def _is_parameter_supported(cls, model_name: str, param_name: str) -> bool:
        """
        Verifica si un parámetro es soportado por el modelo.
        
        Args:
            model_name: Nombre del modelo.
            param_name: Nombre del parámetro a verificar.
            
        Returns:
            bool: True si el parámetro es soportado, False en caso contrario.
        """
        # gpt-5-nano solo soporta: messages, model, max_completion_tokens
        if "gpt-5-nano" in model_name:
            return param_name in ["temperature", "max_completion_tokens", "max_tokens"]
        
        # Para otros modelos, soportar parámetros estándar
        return param_name in ["temperature", "max_tokens", "max_completion_tokens", 
                             "top_p", "frequency_penalty", "presence_penalty"]
    
    @classmethod
    def _call_llm(cls, system_prompt: str, user_prompt: str) -> str:
        """
        Realiza una llamada al LLM con los prompts proporcionados.
        
        Args:
            system_prompt: Prompt del sistema que define el comportamiento.
            user_prompt: Prompt del usuario con la solicitud específica.
            
        Returns:
            str: Respuesta del LLM.
        """
        client = cls._get_client()
        params = cls._get_model_params()
        model_name = params.get("modelo", "gpt-4")
        token_param = cls._get_token_param_name(model_name)
        
        # Parámetros base que siempre se incluyen
        completion_params = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        # Agregar parámetros opcionales solo si son soportados por el modelo
        if "gpt-5-nano" in model_name:
            # gpt-5-nano solo soporta max_completion_tokens, sin temperature ni otros
            completion_params[token_param] = params.get("max_tokens", 1000)
        else:
            # Para otros modelos, incluir todos los parámetros estándar
            completion_params["temperature"] = params.get("temperature", 0.7)
            completion_params[token_param] = params.get("max_tokens", 1000)
            completion_params["top_p"] = params.get("top_p", 0.95)
            completion_params["frequency_penalty"] = params.get("frequency_penalty", 0.0)
            completion_params["presence_penalty"] = params.get("presence_penalty", 0.0)
        
        response = client.chat.completions.create(**completion_params)
        
        return response.choices[0].message.content.strip()
    
    @classmethod
    def generate_description(cls, task_input: task) -> task:
        """
        Genera una descripción para la tarea usando el LLM.
        
        Args:
            task_input: Tarea con description vacía.
            
        Returns:
            task: Tarea con description generada.
        """
        settings = cls._load_settings()
        prompts = settings["system_prompts"]
        base_role = prompts["base_role"]
        desc_config = prompts["description"]
        
        system_prompt = f"{base_role}\n\n{desc_config['instruction']}\n\nIMPORTANTE: La descripción no debe superar las {desc_config['max_words']} palabras."
        
        user_prompt = f"""Genera una descripción para la siguiente tarea:

Título: {task_input.title}
Prioridad: {task_input.priority}
Estado: {task_input.status}
Asignado a: {task_input.assigned_to}
Categoría: {task_input.category or 'No especificada'}
Horas estimadas: {task_input.effort_hours or 'No especificadas'}

Responde únicamente con la descripción, sin encabezados ni explicaciones adicionales."""

        description = cls._call_llm(system_prompt, user_prompt)
        task_input.description = description
        return task_input
    
    @classmethod
    def categorize_task(cls, task_input: task) -> task:
        """
        Categoriza la tarea usando el LLM.
        
        Args:
            task_input: Tarea sin categoría.
            
        Returns:
            task: Tarea con category asignada.
        """
        settings = cls._load_settings()
        prompts = settings["system_prompts"]
        base_role = prompts["base_role"]
        cat_config = prompts["categorize"]
        categories = cls._load_categories()
        
        system_prompt = f"{base_role}\n\n{cat_config['instruction']}"
        
        user_prompt = f"""Clasifica la siguiente tarea:

Título: {task_input.title}
Descripción: {task_input.description}
Prioridad: {task_input.priority}
Asignado a: {task_input.assigned_to}

Categorías disponibles: {', '.join(categories)}

Responde únicamente con el nombre exacto de la categoría."""

        category_response = cls._call_llm(system_prompt, user_prompt)
        
        # Validar que la categoría sea válida
        category_clean = category_response.strip()
        if category_clean in categories:
            task_input.category = category_clean  # type: ignore
        else:
            # Intentar encontrar la categoría más cercana
            for cat in categories:
                if cat.lower() in category_clean.lower():
                    task_input.category = cat  # type: ignore
                    break
            else:
                # Asignar Backend por defecto si no se encuentra
                task_input.category = "Backend"
        
        return task_input
    
    @classmethod
    def estimate_effort(cls, task_input: task) -> task:
        """
        Estima el esfuerzo en horas para la tarea usando el LLM.
        
        Args:
            task_input: Tarea sin effort_hours.
            
        Returns:
            task: Tarea con effort_hours estimado.
        """
        settings = cls._load_settings()
        prompts = settings["system_prompts"]
        base_role = prompts["base_role"]
        est_config = prompts["estimate"]
        
        system_prompt = f"{base_role}\n\n{est_config['instruction']}"
        
        user_prompt = f"""Estima el esfuerzo en horas para la siguiente tarea:

Título: {task_input.title}
Descripción: {task_input.description}
Categoría: {task_input.category or 'No especificada'}
Prioridad: {task_input.priority}
Asignado a: {task_input.assigned_to}

Responde únicamente con un número decimal (ejemplo: 4.5)."""

        effort_response = cls._call_llm(system_prompt, user_prompt)
        
        # Parsear la respuesta a float
        try:
            # Extraer solo números del response
            numbers = re.findall(r'[\d.]+', effort_response)
            if numbers:
                effort_hours = float(numbers[0])
                # Asegurar que sea un valor razonable
                if effort_hours <= 0:
                    effort_hours = 1.0
                elif effort_hours > 1000:
                    effort_hours = 1000.0
                task_input.effort_hours = effort_hours
            else:
                task_input.effort_hours = 4.0  # Valor por defecto
        except (ValueError, IndexError):
            task_input.effort_hours = 4.0  # Valor por defecto
        
        return task_input
    
    @classmethod
    def audit_task(cls, task_input: task) -> task:
        """
        Realiza análisis de riesgos y genera plan de mitigación para la tarea.
        
        Args:
            task_input: Tarea sin risk_analysis ni risk_mitigation.
            
        Returns:
            task: Tarea con risk_analysis y risk_mitigation completados.
        """
        settings = cls._load_settings()
        prompts = settings["system_prompts"]
        base_role = prompts["base_role"]
        risk_config = prompts["risk_analysis"]
        mitigation_config = prompts["risk_mitigation"]
        
        # Primera llamada: Análisis de riesgos
        risk_system_prompt = f"{base_role}\n\n{risk_config['instruction']}\n\nIMPORTANTE: El análisis no debe superar las {risk_config['max_words']} palabras."
        
        risk_user_prompt = f"""Analiza los riesgos de la siguiente tarea:

Título: {task_input.title}
Descripción: {task_input.description}
Categoría: {task_input.category}
Prioridad: {task_input.priority}
Horas estimadas: {task_input.effort_hours}
Estado: {task_input.status}
Asignado a: {task_input.assigned_to}

Proporciona un análisis de riesgos detallado."""

        risk_analysis = cls._call_llm(risk_system_prompt, risk_user_prompt)
        task_input.risk_analysis = risk_analysis
        
        # Segunda llamada: Plan de mitigación
        mitigation_system_prompt = f"{base_role}\n\n{mitigation_config['instruction']}\n\nIMPORTANTE: El plan de mitigación no debe superar las {mitigation_config['max_words']} palabras."
        
        mitigation_user_prompt = f"""Basándote en la siguiente tarea y su análisis de riesgos, genera un plan de mitigación:

INFORMACIÓN DE LA TAREA:
Título: {task_input.title}
Descripción: {task_input.description}
Categoría: {task_input.category}
Prioridad: {task_input.priority}
Horas estimadas: {task_input.effort_hours}
Estado: {task_input.status}
Asignado a: {task_input.assigned_to}

ANÁLISIS DE RIESGOS:
{risk_analysis}

Proporciona un plan de mitigación detallado con acciones preventivas y planes de contingencia."""

        risk_mitigation = cls._call_llm(mitigation_system_prompt, mitigation_user_prompt)
        task_input.risk_mitigation = risk_mitigation
        
        return task_input
