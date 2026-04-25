import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("=== TEST DES VARIABLES D'ENVIRONNEMENT ===")
print(f"TEST_MODE brut: {repr(os.getenv('TEST_MODE'))}")
print(f"TEST_MODE.lower(): {os.getenv('TEST_MODE', '').lower()}")
print(f"Condition TEST_MODE == 'true': {os.getenv('TEST_MODE', '').lower() == 'true'}")
print(f"Condition TEST_MODE.lower() == 'true': {os.getenv('TEST_MODE', '').lower() == 'true'}")
print(f"Condition TEST_MODE.lower() == True: {os.getenv('TEST_MODE', '').lower() == True}")
print("=== FIN TEST ===")
