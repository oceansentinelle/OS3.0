import os
import sys
from dotenv import load_dotenv

# Forcer le mode test avant l'import
os.environ['TEST_MODE'] = 'true'
load_dotenv()

print("=== DÉMARRAGE API EN MODE TEST ===")
print(f"TEST_MODE: {os.getenv('TEST_MODE')}")
print(f"DB_CONFIG sera None: {os.getenv('TEST_MODE', '').lower() in ('true', '1', 'yes')}")

# Importer main après avoir défini TEST_MODE
import main

print(f"TEST_MODE dans main: {main.TEST_MODE}")
print(f"DB_CONFIG dans main: {main.DB_CONFIG}")

if main.TEST_MODE:
    print("✅ MODE TEST ACTIVÉ - Pas de connexion DB")
else:
    print("❌ MODE TEST NON ACTIVÉ - Connexion DB prévue")

print("=== LANCEMENT UVICORN ===")
os.system(f"python -m uvicorn main:app --host 127.0.0.1 --port 8000")
