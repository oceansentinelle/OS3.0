#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel - Script de Requête TimescaleDB
===============================================
Script Python pour exécuter des requêtes SQL sur la base TimescaleDB
et afficher les résultats en format JSON.

Usage:
    python query.py "SELECT * FROM barag.sensor_data LIMIT 5"
    python query.py --file query.sql
    python query.py --interactive

Auteur: Ocean Sentinel Team
Date: 2026-04-16
"""

import sys
import json
import argparse
from datetime import datetime, date
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from pathlib import Path

# Configuration de la connexion
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '6543')),
    'database': os.getenv('DB_NAME', 'oceansentinelle'),
    'user': os.getenv('DB_USER', 'oceansentinel'),
    'password': os.getenv('DB_PASSWORD', ''),
}


class DateTimeEncoder(json.JSONEncoder):
    """Encodeur JSON personnalisé pour gérer les types PostgreSQL."""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def load_env_file(env_path=None):
    """Charge les variables d'environnement depuis un fichier .env."""
    if env_path is None:
        # Chercher .env dans le répertoire parent
        current_dir = Path(__file__).parent.parent
        env_path = current_dir / '.env'
    
    if not env_path.exists():
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Mapper les variables du .env vers DB_CONFIG
                if key == 'POSTGRES_USER':
                    DB_CONFIG['user'] = value
                elif key == 'POSTGRES_PASSWORD':
                    DB_CONFIG['password'] = value
                elif key == 'POSTGRES_DB':
                    DB_CONFIG['database'] = value
                elif key == 'POSTGRES_PORT':
                    DB_CONFIG['port'] = int(value)
    
    return True


def connect_db():
    """Établit une connexion à la base de données."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Erreur de connexion: {e}", file=sys.stderr)
        sys.exit(1)


def execute_query(query, params=None, fetch=True):
    """
    Exécute une requête SQL et retourne les résultats.
    
    Args:
        query (str): Requête SQL à exécuter
        params (tuple): Paramètres pour la requête (optionnel)
        fetch (bool): Si True, retourne les résultats (SELECT), sinon commit (INSERT/UPDATE)
    
    Returns:
        list: Liste de dictionnaires contenant les résultats
    """
    conn = connect_db()
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            
            if fetch:
                results = cursor.fetchall()
                # Convertir RealDictRow en dict standard
                return [dict(row) for row in results]
            else:
                conn.commit()
                return {'affected_rows': cursor.rowcount, 'status': 'success'}
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ Erreur SQL: {e}", file=sys.stderr)
        sys.exit(1)
    
    finally:
        conn.close()


def format_output(results, output_format='json', pretty=True):
    """
    Formate les résultats selon le format demandé.
    
    Args:
        results: Résultats de la requête
        output_format (str): Format de sortie ('json', 'table', 'csv')
        pretty (bool): Si True, formate le JSON de manière lisible
    
    Returns:
        str: Résultats formatés
    """
    if output_format == 'json':
        if pretty:
            return json.dumps(results, cls=DateTimeEncoder, indent=2, ensure_ascii=False)
        else:
            return json.dumps(results, cls=DateTimeEncoder, ensure_ascii=False)
    
    elif output_format == 'table':
        if not results:
            return "Aucun résultat"
        
        # Calculer la largeur des colonnes
        headers = list(results[0].keys())
        col_widths = {h: len(h) for h in headers}
        
        for row in results:
            for header in headers:
                value = str(row[header]) if row[header] is not None else 'NULL'
                col_widths[header] = max(col_widths[header], len(value))
        
        # Construire le tableau
        output = []
        
        # En-tête
        header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
        output.append(header_line)
        output.append("-" * len(header_line))
        
        # Lignes
        for row in results:
            line = " | ".join(
                str(row[h]).ljust(col_widths[h]) if row[h] is not None else 'NULL'.ljust(col_widths[h])
                for h in headers
            )
            output.append(line)
        
        return "\n".join(output)
    
    elif output_format == 'csv':
        if not results:
            return ""
        
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
        
        return output.getvalue()
    
    else:
        return str(results)


def interactive_mode():
    """Mode interactif pour exécuter plusieurs requêtes."""
    print("🌊 Ocean Sentinel - Mode Interactif TimescaleDB")
    print("=" * 60)
    print("Tapez vos requêtes SQL (terminez par ';' et Entrée)")
    print("Commandes spéciales:")
    print("  \\q ou exit  - Quitter")
    print("  \\d          - Lister les tables")
    print("  \\dt         - Lister les tables avec détails")
    print("  \\c          - Afficher la configuration de connexion")
    print("=" * 60)
    print()
    
    conn = connect_db()
    
    try:
        while True:
            try:
                query = input("oceansentinel> ").strip()
                
                if not query:
                    continue
                
                # Commandes spéciales
                if query.lower() in ['\\q', 'exit', 'quit']:
                    print("Au revoir! 👋")
                    break
                
                elif query == '\\d':
                    query = """
                        SELECT schemaname, tablename 
                        FROM pg_tables 
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, tablename;
                    """
                
                elif query == '\\dt':
                    query = """
                        SELECT 
                            schemaname || '.' || tablename AS table,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                        FROM pg_tables
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
                    """
                
                elif query == '\\c':
                    print(f"Host: {DB_CONFIG['host']}")
                    print(f"Port: {DB_CONFIG['port']}")
                    print(f"Database: {DB_CONFIG['database']}")
                    print(f"User: {DB_CONFIG['user']}")
                    continue
                
                # Exécuter la requête
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    
                    if cursor.description:  # SELECT
                        results = [dict(row) for row in cursor.fetchall()]
                        print(format_output(results, output_format='table'))
                        print(f"\n({len(results)} ligne(s))\n")
                    else:  # INSERT/UPDATE/DELETE
                        conn.commit()
                        print(f"✓ Requête exécutée ({cursor.rowcount} ligne(s) affectée(s))\n")
            
            except psycopg2.Error as e:
                conn.rollback()
                print(f"❌ Erreur: {e}\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrompu. Tapez \\q pour quitter.\n")
            
            except EOFError:
                print("\nAu revoir! 👋")
                break
    
    finally:
        conn.close()


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description='Exécute des requêtes SQL sur TimescaleDB Ocean Sentinel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s "SELECT * FROM barag.sensor_data LIMIT 5"
  %(prog)s --file query.sql
  %(prog)s --interactive
  %(prog)s "SELECT COUNT(*) FROM barag.sensor_data" --format table
  %(prog)s --query "SELECT * FROM metadata.stations" --output stations.json
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Requête SQL à exécuter'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Fichier SQL contenant la requête'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Mode interactif'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Fichier de sortie (par défaut: stdout)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'table', 'csv'],
        default='json',
        help='Format de sortie (défaut: json)'
    )
    
    parser.add_argument(
        '--no-pretty',
        action='store_true',
        help='Désactiver le formatage JSON'
    )
    
    parser.add_argument(
        '--host',
        help='Hôte de la base de données'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        help='Port de la base de données'
    )
    
    parser.add_argument(
        '--user',
        help='Utilisateur de la base de données'
    )
    
    parser.add_argument(
        '--password',
        help='Mot de passe (non recommandé, utilisez .env)'
    )
    
    parser.add_argument(
        '--database',
        help='Nom de la base de données'
    )
    
    parser.add_argument(
        '--env-file',
        help='Chemin vers le fichier .env'
    )
    
    args = parser.parse_args()
    
    # Charger les variables d'environnement
    if args.env_file:
        load_env_file(Path(args.env_file))
    else:
        load_env_file()
    
    # Surcharger avec les arguments CLI
    if args.host:
        DB_CONFIG['host'] = args.host
    if args.port:
        DB_CONFIG['port'] = args.port
    if args.user:
        DB_CONFIG['user'] = args.user
    if args.password:
        DB_CONFIG['password'] = args.password
    if args.database:
        DB_CONFIG['database'] = args.database
    
    # Vérifier que le mot de passe est configuré
    if not DB_CONFIG['password']:
        print("❌ Erreur: Mot de passe non configuré", file=sys.stderr)
        print("Configurez DB_PASSWORD dans .env ou utilisez --password", file=sys.stderr)
        sys.exit(1)
    
    # Mode interactif
    if args.interactive:
        interactive_mode()
        return
    
    # Lire la requête depuis un fichier
    if args.file:
        try:
            with open(args.file, 'r') as f:
                query = f.read()
        except IOError as e:
            print(f"❌ Erreur de lecture du fichier: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        sys.exit(1)
    
    # Exécuter la requête
    is_select = query.strip().upper().startswith('SELECT')
    results = execute_query(query, fetch=is_select)
    
    # Formater la sortie
    output = format_output(results, output_format=args.format, pretty=not args.no_pretty)
    
    # Écrire la sortie
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✓ Résultats écrits dans {args.output}")
        except IOError as e:
            print(f"❌ Erreur d'écriture: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == '__main__':
    main()
