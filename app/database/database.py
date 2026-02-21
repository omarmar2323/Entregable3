"""
Configuración de la base de datos MySQL con SQLAlchemy.
Lee la configuración desde settingsApp.json.
"""
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Leer configuración desde settingsApp.json
def load_db_config():
    """
    Carga la configuración de base de datos desde settingsApp.json.
    
    Returns:
        dict: Diccionario con la configuración de base de datos.
    """
    config_file = Path(__file__).resolve().parent.parent.parent / "settingsApp.json"
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config["database"]


# Cargar configuración
db_config = load_db_config()

# Construir URL de conexión MySQL
DATABASE_URL = (
    f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
    f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
)

# Crear engine de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=db_config.get("echo", False),
    pool_size=db_config.get("pool_size", 5),
    max_overflow=db_config.get("max_overflow", 10),
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

# Crear SessionLocal para manejar sesiones
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()


def get_db():
    """
    Generador de dependencia para obtener sesión de base de datos.
    Se usa con FastAPI Depends() para inyectar sesiones en endpoints.
    
    Yields:
        Session: Sesión de SQLAlchemy.
    """
    db = session_local()
    try:
        yield db
    finally:
        db.close()
