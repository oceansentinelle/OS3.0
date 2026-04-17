#!/usr/bin/env python3
"""
============================================================================
Ocean Sentinel Ops - Script de Requêtes Base de Données Production
============================================================================
Description: Se connecte à TimescaleDB sur le VPS pour exécuter des requêtes
             en lecture seule et retourner les résultats en JSON
Usage: python query_prod_db.py [query_type]
Query Types: count, today, last, stats, health
============================================================================
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from dotenv import load_dotenv
except ImportError:
    print(json.dumps({
        "error": "Dépendances manquantes",
        "message": "Installez: pip install psycopg2-binary python-dotenv",
        "success": False
    }, indent=2))
    sys.exit(1)

# Couleurs pour l'affichage console
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}", file=sys.stderr)

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}", file=sys.stderr)

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}", file=sys.stderr)

def load_config() -> Dict[str, str]:
    """Charge la configuration depuis .env.vps"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent
    env_file = project_root / ".env.vps"
    
    if not env_file.exists():
        print_error(f"Fichier .env.vps non trouvé: {env_file}")
        print_info("Créez le fichier .env.vps à la racine du projet avec:")
        print("DB_HOST=76.13.43.3")
        print("DB_PORT=6543")
        print("DB_NAME=oceansentinelle")
        print("DB_USER=oceansentinel")
        print("DB_PASSWORD=VotreMotDePasse")
        sys.exit(1)
    
    load_dotenv(env_file)
    
    config = {
        'host': os.getenv('DB_HOST', '76.13.43.3'),
        'port': int(os.getenv('DB_PORT', '6543')),
        'database': os.getenv('DB_NAME', 'oceansentinelle'),
        'user': os.getenv('DB_USER', 'oceansentinel'),
        'password': os.getenv('DB_PASSWORD', ''),
    }
    
    if not config['password']:
        print_error("DB_PASSWORD non défini dans .env.vps")
        sys.exit(1)
    
    return config

def connect_db(config: Dict[str, str]) -> Optional[psycopg2.extensions.connection]:
    """Établit une connexion à la base de données"""
    try:
        print_info(f"Connexion à {config['host']}:{config['port']}/{config['database']}...")
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            connect_timeout=10
        )
        print_success("Connexion établie")
        return conn
    except psycopg2.OperationalError as e:
        print_error(f"Erreur de connexion: {e}")
        return None
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        return None

def query_count(conn) -> Dict[str, Any]:
    """Compte le nombre total d'enregistrements"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM barag.sensor_data;")
            result = cursor.fetchone()
            
            return {
                "success": True,
                "query": "count",
                "data": {
                    "total_records": result['total']
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "query": "count",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def query_today(conn) -> Dict[str, Any]:
    """Compte les enregistrements du jour"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as today_count
                FROM barag.sensor_data
                WHERE time >= CURRENT_DATE;
            """)
            result = cursor.fetchone()
            
            return {
                "success": True,
                "query": "today",
                "data": {
                    "today_records": result['today_count'],
                    "date": datetime.now().date().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "query": "today",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def query_last(conn) -> Dict[str, Any]:
    """Récupère les 5 dernières données insérées"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    time,
                    station_id,
                    temperature_water,
                    salinity,
                    quality_flag,
                    data_source
                FROM barag.sensor_data
                ORDER BY time DESC
                LIMIT 5;
            """)
            results = cursor.fetchall()
            
            # Convertir les résultats en format sérialisable
            records = []
            for row in results:
                records.append({
                    "time": row['time'].isoformat() if row['time'] else None,
                    "station_id": row['station_id'],
                    "temperature_water": float(row['temperature_water']) if row['temperature_water'] else None,
                    "salinity": float(row['salinity']) if row['salinity'] else None,
                    "quality_flag": row['quality_flag'],
                    "data_source": row['data_source']
                })
            
            return {
                "success": True,
                "query": "last",
                "data": {
                    "count": len(records),
                    "records": records
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "query": "last",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def query_stats(conn) -> Dict[str, Any]:
    """Récupère des statistiques complètes"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Statistiques générales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    MIN(time) as first_record,
                    MAX(time) as last_record,
                    COUNT(DISTINCT station_id) as stations_count
                FROM barag.sensor_data;
            """)
            general = cursor.fetchone()
            
            # Données du jour
            cursor.execute("""
                SELECT COUNT(*) as today_count
                FROM barag.sensor_data
                WHERE time >= CURRENT_DATE;
            """)
            today = cursor.fetchone()
            
            # Qualité des données
            cursor.execute("""
                SELECT 
                    quality_flag,
                    COUNT(*) as count
                FROM barag.sensor_data
                GROUP BY quality_flag
                ORDER BY quality_flag;
            """)
            quality = cursor.fetchall()
            
            return {
                "success": True,
                "query": "stats",
                "data": {
                    "total_records": general['total_records'],
                    "first_record": general['first_record'].isoformat() if general['first_record'] else None,
                    "last_record": general['last_record'].isoformat() if general['last_record'] else None,
                    "stations_count": general['stations_count'],
                    "today_records": today['today_count'],
                    "quality_distribution": [
                        {"flag": row['quality_flag'], "count": row['count']}
                        for row in quality
                    ]
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "query": "stats",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def query_health(conn) -> Dict[str, Any]:
    """Vérifie la santé de la base de données"""
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Vérifier la connexion
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            # Vérifier la table
            cursor.execute("""
                SELECT COUNT(*) as total FROM barag.sensor_data;
            """)
            count = cursor.fetchone()
            
            # Vérifier la dernière insertion
            cursor.execute("""
                SELECT MAX(time) as last_insert FROM barag.sensor_data;
            """)
            last = cursor.fetchone()
            
            last_insert = last['last_insert']
            hours_since_last = None
            if last_insert:
                hours_since_last = (datetime.now(last_insert.tzinfo) - last_insert).total_seconds() / 3600
            
            return {
                "success": True,
                "query": "health",
                "data": {
                    "database_version": version['version'],
                    "connection_ok": True,
                    "table_accessible": True,
                    "total_records": count['total'],
                    "last_insert": last_insert.isoformat() if last_insert else None,
                    "hours_since_last_insert": round(hours_since_last, 2) if hours_since_last else None,
                    "status": "healthy" if hours_since_last and hours_since_last < 24 else "warning"
                },
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "query": "health",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Point d'entrée principal"""
    query_type = sys.argv[1] if len(sys.argv) > 1 else "count"
    
    print_info(f"Type de requête: {query_type}")
    
    # Charger la configuration
    config = load_config()
    
    # Se connecter à la base
    conn = connect_db(config)
    if not conn:
        result = {
            "success": False,
            "error": "Impossible de se connecter à la base de données",
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)
    
    try:
        # Exécuter la requête appropriée
        if query_type == "count":
            result = query_count(conn)
        elif query_type == "today":
            result = query_today(conn)
        elif query_type == "last":
            result = query_last(conn)
        elif query_type == "stats":
            result = query_stats(conn)
        elif query_type == "health":
            result = query_health(conn)
        else:
            result = {
                "success": False,
                "error": f"Type de requête inconnu: {query_type}",
                "available_queries": ["count", "today", "last", "stats", "health"],
                "timestamp": datetime.now().isoformat()
            }
        
        # Afficher le résultat en JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result['success']:
            print_success("Requête exécutée avec succès")
            sys.exit(0)
        else:
            print_error("Erreur lors de l'exécution de la requête")
            sys.exit(1)
            
    finally:
        conn.close()
        print_info("Connexion fermée")

if __name__ == "__main__":
    main()
