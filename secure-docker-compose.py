#!/usr/bin/env python3
"""
Script de Sécurisation Automatique - docker-compose.yml
Ocean Sentinel - ABACODE 2.0

Objectif: Remplacer tous les ports 0.0.0.0 par 127.0.0.1
pour éviter l'exposition publique des services internes

Usage:
    python3 secure-docker-compose.py
"""

import re
import sys
from datetime import datetime
from pathlib import Path

# Configuration
COMPOSE_FILE = Path("/opt/oceansentinel/docker-compose.yml")
BACKUP_DIR = Path("/opt/oceansentinel/backups")

def create_backup(file_path):
    """Créer une sauvegarde horodatée du fichier"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = BACKUP_DIR / f"docker-compose.yml.backup-{timestamp}"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    return backup_path

def secure_ports(content):
    """Remplacer 0.0.0.0 par 127.0.0.1 dans les ports"""
    # Pattern pour détecter les ports exposés
    pattern = r'(\s+- ["\']?)0\.0\.0\.0:(\d+(?:-\d+)?:\d+(?:-\d+)?)'
    
    # Compter les occurrences
    matches = re.findall(pattern, content)
    count = len(matches)
    
    # Effectuer le remplacement
    secured_content = re.sub(pattern, r'\g<1>127.0.0.1:\g<2>', content)
    
    return secured_content, count

def main():
    print("=" * 60)
    print("SÉCURISATION AUTOMATIQUE - docker-compose.yml")
    print("Ocean Sentinel - ABACODE 2.0")
    print("=" * 60)
    print()
    
    # Vérifier que le fichier existe
    if not COMPOSE_FILE.exists():
        print(f"❌ ERREUR: Fichier {COMPOSE_FILE} introuvable")
        sys.exit(1)
    
    print(f"✅ Fichier trouvé: {COMPOSE_FILE}")
    print()
    
    # Lire le contenu
    with open(COMPOSE_FILE, 'r') as f:
        original_content = f.read()
    
    # Afficher les ports actuels
    print("🔍 Ports actuellement exposés:")
    for i, line in enumerate(original_content.split('\n'), 1):
        if '0.0.0.0:' in line:
            print(f"   Ligne {i}: {line.strip()}")
    print()
    
    # Créer une sauvegarde
    print("📦 Création d'une sauvegarde...")
    backup_path = create_backup(COMPOSE_FILE)
    print(f"✅ Sauvegarde créée: {backup_path}")
    print()
    
    # Sécuriser les ports
    secured_content, count = secure_ports(original_content)
    
    if count == 0:
        print("✅ Aucune modification nécessaire - Tous les ports sont déjà sécurisés")
        sys.exit(0)
    
    print(f"⚠️  {count} port(s) à sécuriser")
    print()
    
    # Écrire le nouveau contenu
    print("🔧 Application des modifications...")
    with open(COMPOSE_FILE, 'w') as f:
        f.write(secured_content)
    
    print("✅ Modifications appliquées avec succès!")
    print()
    
    # Afficher les nouveaux ports
    print("🔍 Ports sécurisés:")
    for i, line in enumerate(secured_content.split('\n'), 1):
        if '127.0.0.1:' in line and 'ports:' not in line.lower():
            print(f"   Ligne {i}: {line.strip()}")
    print()
    
    # Vérifier qu'il ne reste plus de 0.0.0.0
    remaining = secured_content.count('0.0.0.0:')
    if remaining > 0:
        print(f"⚠️  ATTENTION: {remaining} occurrence(s) de 0.0.0.0 restante(s)")
    else:
        print("✅ Tous les ports 0.0.0.0 ont été remplacés")
    
    print()
    print("=" * 60)
    print("✅ SÉCURISATION TERMINÉE")
    print("=" * 60)
    print()
    print("📋 Résumé:")
    print(f"   - Ports sécurisés: {count}")
    print(f"   - Sauvegarde: {backup_path}")
    print()
    print("🚀 Prochaines étapes:")
    print("   1. Redémarrer les services:")
    print("      cd /opt/oceansentinel")
    print("      docker compose down")
    print("      docker compose up -d")
    print()
    print("   2. Vérifier les ports:")
    print("      netstat -tlnp | grep -E ':(5432|6379|8000|9000)'")
    print()
    print("   3. Tester l'API:")
    print("      curl http://127.0.0.1:8000/health")
    print()
    print("⚠️  IMPORTANT: Configurez Nginx comme reverse proxy")
    print("   pour exposer l'API publiquement de manière sécurisée")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        sys.exit(1)
