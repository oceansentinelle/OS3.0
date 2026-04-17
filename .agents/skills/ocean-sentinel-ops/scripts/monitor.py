#!/usr/bin/env python3
"""
============================================================================
Ocean Sentinel Ops - Script de Monitoring VPS
============================================================================
Description: Interroge l'API REST distante et vérifie l'état du VPS
Usage: python monitor.py [--vps-ip IP] [--api-port PORT]
============================================================================
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import requests
except ImportError:
    print(json.dumps({
        "error": "Module 'requests' manquant",
        "message": "Installez: pip install requests",
        "success": False
    }, indent=2))
    sys.exit(1)

# Couleurs pour l'affichage console
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}", file=sys.stderr)

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}", file=sys.stderr)

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}", file=sys.stderr)

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}", file=sys.stderr)

def print_header(msg: str):
    print(f"{Colors.CYAN}{'='*80}{Colors.NC}", file=sys.stderr)
    print(f"{Colors.CYAN}{msg}{Colors.NC}", file=sys.stderr)
    print(f"{Colors.CYAN}{'='*80}{Colors.NC}", file=sys.stderr)

def check_api_health(vps_ip: str, api_port: int = 8000) -> Dict[str, Any]:
    """
    Vérifie la santé de l'API REST
    
    Args:
        vps_ip: Adresse IP du VPS
        api_port: Port de l'API (défaut: 8000)
    
    Returns:
        Dictionnaire avec le statut de santé
    """
    url = f"http://{vps_ip}:{api_port}/health"
    
    try:
        print_info(f"Interrogation de l'API: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "api_status": "healthy",
            "api_url": url,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "api_status": "unreachable",
            "api_url": url,
            "error": "Impossible de se connecter à l'API",
            "timestamp": datetime.now().isoformat()
        }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "api_status": "timeout",
            "api_url": url,
            "error": "Timeout lors de la connexion à l'API",
            "timestamp": datetime.now().isoformat()
        }
    
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "api_status": "error",
            "api_url": url,
            "error": f"Erreur HTTP: {e}",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "api_status": "error",
            "api_url": url,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def check_sacs_alerts(vps_ip: str, api_port: int = 8000) -> Dict[str, Any]:
    """
    Vérifie les alertes SACS
    
    Args:
        vps_ip: Adresse IP du VPS
        api_port: Port de l'API (défaut: 8000)
    
    Returns:
        Dictionnaire avec les alertes SACS
    """
    url = f"http://{vps_ip}:{api_port}/api/v1/alerts/sacs"
    
    try:
        print_info(f"Vérification des alertes SACS: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "alerts_checked": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "alerts_checked": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def check_latest_measurement(vps_ip: str, station_id: str = "VPS_PROD", api_port: int = 8000) -> Dict[str, Any]:
    """
    Récupère la dernière mesure d'une station
    
    Args:
        vps_ip: Adresse IP du VPS
        station_id: ID de la station
        api_port: Port de l'API (défaut: 8000)
    
    Returns:
        Dictionnaire avec la dernière mesure
    """
    url = f"http://{vps_ip}:{api_port}/api/v1/station/{station_id}/latest"
    
    try:
        print_info(f"Récupération dernière mesure: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "measurement_found": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "success": True,
                "measurement_found": False,
                "message": f"Aucune donnée pour la station {station_id}",
                "timestamp": datetime.now().isoformat()
            }
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def generate_report(health: Dict, alerts: Dict, latest: Dict) -> Dict[str, Any]:
    """
    Génère un rapport complet de monitoring
    
    Args:
        health: Résultat du health check
        alerts: Résultat des alertes SACS
        latest: Résultat de la dernière mesure
    
    Returns:
        Rapport complet
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "healthy" if health["success"] else "unhealthy",
        "api": {
            "status": health.get("api_status", "unknown"),
            "reachable": health["success"]
        },
        "database": {},
        "alerts": {
            "checked": alerts.get("alerts_checked", False),
            "total": 0,
            "critical": 0,
            "warning": 0
        },
        "latest_measurement": {
            "found": latest.get("measurement_found", False)
        }
    }
    
    # Informations base de données
    if health["success"] and "data" in health:
        report["database"] = {
            "status": health["data"].get("database", "unknown"),
            "total_records": health["data"].get("total_records", 0)
        }
    
    # Alertes SACS
    if alerts["success"] and "data" in alerts:
        alert_data = alerts["data"]
        report["alerts"]["total"] = alert_data.get("total_alerts", 0)
        
        # Compter les alertes par niveau
        for alert_type in ["ph", "oxygen"]:
            if alert_type in alert_data.get("alerts", {}):
                for alert in alert_data["alerts"][alert_type]:
                    if alert.get("level") == "critical":
                        report["alerts"]["critical"] += 1
                    elif alert.get("level") == "warning":
                        report["alerts"]["warning"] += 1
    
    # Dernière mesure
    if latest["success"] and latest.get("measurement_found") and "data" in latest:
        meas = latest["data"]
        report["latest_measurement"] = {
            "found": True,
            "time": meas.get("time"),
            "station_id": meas.get("station_id"),
            "temperature": meas.get("temperature_water"),
            "salinity": meas.get("salinity"),
            "quality_flag": meas.get("quality_flag")
        }
    
    return report

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Ocean Sentinel Ops - Monitoring VPS"
    )
    parser.add_argument(
        "--vps-ip",
        default="76.13.43.3",
        help="Adresse IP du VPS (défaut: 76.13.43.3)"
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="Port de l'API (défaut: 8000)"
    )
    parser.add_argument(
        "--station-id",
        default="VPS_PROD",
        help="ID de la station (défaut: VPS_PROD)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Sortie en JSON uniquement"
    )
    
    args = parser.parse_args()
    
    if not args.json:
        print_header("OCEAN SENTINEL OPS - MONITORING VPS")
        print_info(f"VPS: {args.vps_ip}:{args.api_port}")
        print("")
    
    # Vérifications
    health = check_api_health(args.vps_ip, args.api_port)
    alerts = check_sacs_alerts(args.vps_ip, args.api_port)
    latest = check_latest_measurement(args.vps_ip, args.station_id, args.api_port)
    
    # Générer le rapport
    report = generate_report(health, alerts, latest)
    
    # Affichage
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("")
        print_header("RAPPORT DE MONITORING")
        print("")
        
        # Statut général
        if report["overall_status"] == "healthy":
            print_success(f"Statut général: {report['overall_status'].upper()}")
        else:
            print_error(f"Statut général: {report['overall_status'].upper()}")
        
        print("")
        
        # API
        print_info("API REST:")
        if report["api"]["reachable"]:
            print_success(f"  Statut: {report['api']['status']}")
        else:
            print_error(f"  Statut: {report['api']['status']}")
        
        print("")
        
        # Base de données
        print_info("Base de données:")
        if report["database"]:
            print_success(f"  Statut: {report['database'].get('status', 'unknown')}")
            print_info(f"  Total enregistrements: {report['database'].get('total_records', 0)}")
        else:
            print_warning("  Statut: Non disponible")
        
        print("")
        
        # Alertes SACS
        print_info("Alertes SACS:")
        if report["alerts"]["checked"]:
            total = report["alerts"]["total"]
            critical = report["alerts"]["critical"]
            warning = report["alerts"]["warning"]
            
            if total == 0:
                print_success(f"  Aucune alerte active")
            else:
                if critical > 0:
                    print_error(f"  🔴 {critical} alerte(s) CRITICAL")
                if warning > 0:
                    print_warning(f"  ⚠️  {warning} alerte(s) WARNING")
        else:
            print_warning("  Vérification non disponible")
        
        print("")
        
        # Dernière mesure
        print_info("Dernière mesure:")
        if report["latest_measurement"]["found"]:
            meas = report["latest_measurement"]
            print_success(f"  Station: {meas.get('station_id', 'N/A')}")
            print_info(f"  Timestamp: {meas.get('time', 'N/A')}")
            print_info(f"  Température: {meas.get('temperature', 'N/A')} °C")
            print_info(f"  Salinité: {meas.get('salinity', 'N/A')} PSU")
            print_info(f"  Qualité: QC={meas.get('quality_flag', 'N/A')}")
        else:
            print_warning("  Aucune mesure disponible")
        
        print("")
        print_header("FIN DU RAPPORT")
    
    # Code de sortie
    sys.exit(0 if report["overall_status"] == "healthy" else 1)

if __name__ == "__main__":
    main()
