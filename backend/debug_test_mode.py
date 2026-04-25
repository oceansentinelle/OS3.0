import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=== DEBUG TEST_MODE ===")
print(f"TEST_MODE: {repr(os.getenv('TEST_MODE'))}")
print(f"TEST_MODE.lower(): {os.getenv('TEST_MODE', '').lower()}")
print(f"TEST_MODE in ('true', '1', 'yes'): {os.getenv('TEST_MODE', '') in ('true', '1', 'yes')}")

# Simulation de la logique du main.py
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() in ('true', '1', 'yes')
print(f"TEST_MODE calculé: {TEST_MODE}")
print(f"not TEST_MODE: {not TEST_MODE}")

if not TEST_MODE:
    print("→ Connexion à la base de données")
else:
    print("→ MODE TEST LOCAL - Sans base de données")
print("=== FIN DEBUG ===")
