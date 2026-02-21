#!/usr/bin/env python
"""Test script para generar tareas de historia de usuario."""

import sys
import os
import requests
sys.path.insert(0, os.getcwd())

from app.database.database import session_local
from app.database.models import user_story

# Obtener la última historia de usuario
db = session_local()
try:
    stories = db.query(user_story).order_by(user_story.id.desc()).limit(1).all()
    
    if stories:
        latest_story = stories[0]
        print(f"[TEST] Última historia: ID={latest_story.id}, Proyecto={latest_story.project}")
        print(f"[TEST] Intentando generar tareas...")
        
        # Hacer POST al endpoint /user-stories/{id}/generate-tasks
        url = f"http://127.0.0.1:8000/user-stories/{latest_story.id}/generate-tasks"
        print(f"[TEST] POST: {url}")
        
        response = requests.post(url)
        print(f"[TEST] Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"[TEST] Respuesta:")
            print(response.text[:1000])
        else:
            print(f"[TEST] ✅ Tareas generadas exitosamente")
            print(f"[TEST] URL final: {response.url}")
    else:
        print("[TEST] ❌ No hay historias en BD")
finally:
    db.close()
