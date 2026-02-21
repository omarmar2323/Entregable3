"""
Script para inicializar la base de datos.
Crea la base de datos si no existe y luego crea todas las tablas definidas en los modelos SQLAlchemy.
"""
import json
from pathlib import Path
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database.database import Base, load_db_config
from app.database.models import user_story, task, category


def create_database_if_not_exists():
    """
    Crea la base de datos si no existe.
    Se conecta a MySQL sin especificar base de datos y la crea si es necesario.
    """
    db_config = load_db_config()
    
    # Conectar a MySQL sin especificar base de datos
    connection = None
    try:
        print(f"🔍 Verificando base de datos '{db_config['database']}'...")
        connection = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Verificar si la base de datos existe
            cursor.execute(
                f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_config['database']}'"
            )
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Base de datos '{db_config['database']}' ya existe")
            else:
                # Crear la base de datos
                print(f"📦 Creando base de datos '{db_config['database']}'...")
                cursor.execute(
                    f"CREATE DATABASE {db_config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                print(f"✅ Base de datos '{db_config['database']}' creada exitosamente!")
        
        connection.commit()
        
    except pymysql.Error as e:
        print(f"❌ Error al crear la base de datos: {e}")
        raise
    finally:
        if connection:
            connection.close()


def insert_initial_categories(engine):
    """
    Inserta las categorías iniciales en la base de datos.
    
    Args:
        engine: Motor de SQLAlchemy conectado a la BD
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Categorías iniciales
        initial_categories = [
            {"name": "Backend", "description": "Tareas de desarrollo del backend"},
            {"name": "Frontend", "description": "Tareas de desarrollo del frontend"},
            {"name": "Database", "description": "Tareas relacionadas con base de datos"},
            {"name": "DevOps", "description": "Tareas de operaciones y despliegue"},
            {"name": "Infrastructure", "description": "Tareas de infraestructura"},
            {"name": "Testing", "description": "Tareas de pruebas y QA"},
            {"name": "Documentation", "description": "Tareas de documentación"},
            {"name": "Security", "description": "Tareas de seguridad"},
            {"name": "Performance", "description": "Tareas de optimización y rendimiento"},
            {"name": "UI/UX", "description": "Tareas de diseño de interfaz y experiencia"},
            {"name": "API", "description": "Tareas de desarrollo de API"},
            {"name": "Mobile", "description": "Tareas de desarrollo mobile"},
            {"name": "Architecture", "description": "Tareas de arquitectura del sistema"},
            {"name": "Maintenance", "description": "Tareas de mantenimiento"},
            {"name": "Bug Fix", "description": "Corrección de errores y bugs"},
            {"name": "Feature", "description": "Nuevas funcionalidades"},
            {"name": "Refactoring", "description": "Mejora y refactorización de código"},
            {"name": "Integration", "description": "Tareas de integración"},
            {"name": "Deployment", "description": "Tareas de despliegue"},
            {"name": "Monitoring", "description": "Tareas de monitoreo y observabilidad"},
        ]
        
        # Verificar si ya existen categorías
        existing_count = session.query(category).count()
        
        if existing_count == 0:
            print("📥 Insertando categorías iniciales...")
            for cat_data in initial_categories:
                new_category = category(
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                session.add(new_category)
            
            session.commit()
            print(f"✅ {len(initial_categories)} categorías insertadas exitosamente!")
        else:
            print(f"ℹ️  Ya existen {existing_count} categorías en la base de datos")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error al insertar categorías: {e}")
        raise
    finally:
        session.close()


def init_db():
    """
    Inicializa la base de datos completa:
    1. Crea la base de datos si no existe
    2. Crea todas las tablas definidas en los modelos
    3. Inserta categorías iniciales
    """
    print("🔧 Inicializando base de datos...")
    print()
    
    # Paso 1: Crear base de datos si no existe
    create_database_if_not_exists()
    print()
    
    # Paso 2: Crear tablas
    db_config = load_db_config()
    DATABASE_URL = (
        f"mysql+pymysql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    print("📋 Creando tablas...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Tablas creadas exitosamente!")
    print()
    
    # Paso 3: Insertar categorías iniciales
    insert_initial_categories(engine)
    print()
    
    print("📊 Tablas disponibles:")
    print("   • user_stories")
    print("   • tasks")
    print("   • categories")
    print()
    print("🎉 Inicialización completada!")


if __name__ == "__main__":
    init_db()
