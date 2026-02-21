from functools import lru_cache
import json
from pathlib import Path
from pydantic import BaseModel


class app_settings(BaseModel):
    """
    Configuración principal de la aplicación FastAPI.

    Atributos:
        app_name (str): Nombre de la aplicación.
        app_version (str): Versión de la API.
        app_description (str): Descripción breve usada en Swagger/OpenAPI.
    """
    app_name: str = "gestor_de_tareas_fastapi"
    app_version: str = "2.0.0"
    app_description: str = (
        "api_rest_para_la_gestion_de_tareas_y_historias_de_usuario_con_base_de_datos_mysql"
    )


def load_app_settings_from_file() -> app_settings:
    """
    Carga la configuración de la aplicación desde settingsApp.json.
    Si el archivo no existe, usa valores por defecto.
    
    Returns:
        app_settings: Configuración de la aplicación.
    """
    try:
        config_file = Path(__file__).resolve().parent.parent.parent / "settingsApp.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                app_config = config.get("app", {})
                return app_settings(
                    app_name=app_config.get("name", "gestor_de_tareas_fastapi"),
                    app_version=app_config.get("version", "2.0.0"),
                    app_description=app_config.get("description", "api_rest_para_la_gestion_de_tareas_y_historias_de_usuario_con_base_de_datos_mysql")
                )
    except Exception:
        pass
    return app_settings()


@lru_cache
def get_settings() -> app_settings:
    """
    Devuelve la configuración de la aplicación como singleton (con cache).
    Returns:
        app_settings: Instancia única de configuración.
    """
    return load_app_settings_from_file()




