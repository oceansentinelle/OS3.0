#!/usr/bin/env python3
"""
================================================================================
Connecteur Hub'Eau
================================================================================

Connecteur pour l'API Qualité des Cours d'Eau de Hub'Eau.

Source: https://hubeau.eaufrance.fr/page/api-qualite-cours-deau

Fonctionnalités:
- Recherche stations
- Récupération analyses qualité eau
- Pagination automatique (limite 20 000 enregistrements)
- Découpage requêtes pour rester sous limites
- Export JSON/GeoJSON/CSV

Limites documentées:
- Profondeur max: 20 000 enregistrements
- Nécessite découpage requêtes discriminantes
- Synchronisation continue avec Naïades

Conformité:
- Collecte incrémentale
- Retry avec backoff
- Timeout 30s
- Logging structuré
================================================================================
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class HubEauConnector(BaseConnector):
    """Connecteur Hub'Eau API Qualité Cours d'Eau."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get(
            'base_url',
            'https://hubeau.eaufrance.fr/api/v2/qualite_rivieres'
        )
        self.max_results_per_request = 20000  # Limite Hub'Eau
        self.page_size = 1000  # Taille page pour pagination
        
    def search_stations(
        self,
        bbox: tuple = None,
        commune: str = None,
        departement: str = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche stations de mesure.
        
        Args:
            bbox: Bounding box (lon_min, lat_min, lon_max, lat_max)
            commune: Code commune INSEE
            departement: Code département
            
        Returns:
            Liste de stations
        """
        url = f"{self.base_url}/station_pc"
        
        params = {
            'format': 'json',
            'size': self.page_size,
        }
        
        if bbox:
            lon_min, lat_min, lon_max, lat_max = bbox
            params['bbox'] = f"{lon_min},{lat_min},{lon_max},{lat_max}"
        
        if commune:
            params['code_commune'] = commune
        
        if departement:
            params['code_departement'] = departement
        
        stations = []
        page = 1
        
        while True:
            params['page'] = page
            
            logger.info(f"Recherche stations Hub'Eau (page {page})...")
            
            response = self._make_request(url, params)
            data = response.json()
            
            if 'data' not in data or not data['data']:
                break
            
            stations.extend(data['data'])
            
            # Vérifier s'il y a d'autres pages
            if len(data['data']) < self.page_size:
                break
            
            page += 1
        
        logger.info(f"✅ {len(stations)} stations trouvées")
        
        return stations
    
    def fetch_data(
        self,
        start_time: datetime,
        end_time: datetime,
        station_codes: List[str] = None,
        parameters: List[str] = None,
        bbox: tuple = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère analyses qualité eau.
        
        IMPORTANT: Hub'Eau limite à 20 000 enregistrements.
        Si la requête dépasse, il faut découper par:
        - Période plus courte
        - Stations spécifiques
        - Paramètres spécifiques
        
        Args:
            start_time: Début période
            end_time: Fin période
            station_codes: Codes stations (découpage recommandé)
            parameters: Codes paramètres (découpage recommandé)
            bbox: Bounding box géographique
            
        Returns:
            Liste d'analyses
        """
        logger.info(
            f"Récupération Hub'Eau: "
            f"[{start_time.isoformat()} - {end_time.isoformat()}]"
        )
        
        # Stratégie de découpage si nécessaire
        if not station_codes and not parameters:
            logger.warning(
                "⚠️  Requête large sans découpage - risque de dépasser 20 000 enregistrements"
            )
        
        url = f"{self.base_url}/analyse_pc"
        
        params = {
            'format': 'json',
            'size': self.page_size,
            'date_debut_prelevement': start_time.strftime('%Y-%m-%d'),
            'date_fin_prelevement': end_time.strftime('%Y-%m-%d'),
        }
        
        if station_codes:
            params['code_station'] = ','.join(station_codes)
        
        if parameters:
            params['code_parametre'] = ','.join(parameters)
        
        if bbox:
            lon_min, lat_min, lon_max, lat_max = bbox
            params['bbox'] = f"{lon_min},{lat_min},{lon_max},{lat_max}"
        
        analyses = []
        page = 1
        
        while True:
            params['page'] = page
            
            logger.info(f"Récupération analyses Hub'Eau (page {page})...")
            
            response = self._make_request(url, params)
            data = response.json()
            
            if 'data' not in data or not data['data']:
                break
            
            page_data = data['data']
            analyses.extend(page_data)
            
            # Vérifier limite 20 000
            if len(analyses) >= self.max_results_per_request:
                logger.warning(
                    f"⚠️  Limite Hub'Eau atteinte ({self.max_results_per_request} enregistrements) - "
                    "découpage requis"
                )
                break
            
            # Vérifier s'il y a d'autres pages
            if len(page_data) < self.page_size:
                break
            
            page += 1
        
        logger.info(f"✅ {len(analyses)} analyses récupérées")
        
        # Convertir vers modèle canonique
        measurements = self._convert_to_measurements(analyses)
        
        return measurements
    
    def fetch_data_chunked(
        self,
        start_time: datetime,
        end_time: datetime,
        station_codes: List[str] = None,
        chunk_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Récupère données avec découpage temporel automatique.
        
        Stratégie pour éviter la limite 20 000:
        - Découper par périodes de chunk_days jours
        - Traiter chaque chunk séparément
        
        Args:
            start_time: Début période
            end_time: Fin période
            station_codes: Codes stations
            chunk_days: Taille chunk en jours
            
        Returns:
            Liste d'analyses (toutes périodes)
        """
        all_measurements = []
        
        current_start = start_time
        
        while current_start < end_time:
            current_end = min(
                current_start + timedelta(days=chunk_days),
                end_time
            )
            
            logger.info(
                f"📅 Chunk: {current_start.date()} → {current_end.date()}"
            )
            
            chunk_measurements = self.fetch_data(
                current_start,
                current_end,
                station_codes=station_codes
            )
            
            all_measurements.extend(chunk_measurements)
            
            current_start = current_end
        
        logger.info(
            f"✅ Total chunked: {len(all_measurements)} mesures "
            f"({(end_time - start_time).days} jours)"
        )
        
        return all_measurements
    
    def _convert_to_measurements(
        self,
        analyses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convertit analyses Hub'Eau vers modèle canonique.
        
        Structure Hub'Eau:
        - code_station
        - date_prelevement
        - code_parametre
        - libelle_parametre
        - resultat
        - symbole_unite
        """
        measurements = []
        
        for analyse in analyses:
            measurement = {
                'station_id': analyse.get('code_station'),
                'timestamp_utc': self._parse_hubeau_date(
                    analyse.get('date_prelevement')
                ),
                'variable': self._normalize_parameter(
                    analyse.get('code_parametre'),
                    analyse.get('libelle_parametre')
                ),
                'raw_value': self._parse_result(analyse.get('resultat')),
                'raw_unit': analyse.get('symbole_unite', ''),
                'source_name': 'HubEau',
                'metadata': {
                    'code_parametre': analyse.get('code_parametre'),
                    'libelle_parametre': analyse.get('libelle_parametre'),
                    'code_remarque': analyse.get('code_remarque'),
                    'mnemonique_remarque': analyse.get('mnemonique_remarque'),
                }
            }
            
            measurements.append(measurement)
        
        return measurements
    
    def _parse_hubeau_date(self, date_str: str) -> datetime:
        """Parse date Hub'Eau (format ISO 8601)."""
        if not date_str:
            return None
        
        # Hub'Eau retourne ISO 8601: 2024-01-15T10:30:00Z
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    def _parse_result(self, result_str: str) -> Optional[float]:
        """Parse résultat analyse (peut contenir '<' ou '>')."""
        if not result_str:
            return None
        
        # Nettoyer symboles
        cleaned = result_str.replace('<', '').replace('>', '').strip()
        
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Impossible de parser résultat: {result_str}")
            return None
    
    def _normalize_parameter(
        self,
        code_parametre: str,
        libelle_parametre: str
    ) -> str:
        """
        Normalise code paramètre Hub'Eau vers nom canonique.
        
        Exemples:
        - 1301 (Température) → temperature
        - 1302 (pH) → ph
        - 1303 (Conductivité) → conductivity
        - 1311 (Oxygène dissous) → dissolved_oxygen
        """
        # Mapping codes Sandre vers noms canoniques
        mapping = {
            '1301': 'temperature',
            '1302': 'ph',
            '1303': 'conductivity',
            '1311': 'dissolved_oxygen',
            '1313': 'salinity',
            '1335': 'turbidity',
            '1340': 'suspended_matter',
            '1433': 'nitrate',
            '1350': 'phosphate',
        }
        
        if code_parametre in mapping:
            return mapping[code_parametre]
        
        # Fallback: utiliser libellé nettoyé
        if libelle_parametre:
            return libelle_parametre.lower().replace(' ', '_')
        
        return f"param_{code_parametre}"
    
    def get_available_parameters(self) -> List[Dict[str, Any]]:
        """
        Récupère liste des paramètres disponibles.
        
        Returns:
            Liste de paramètres
        """
        url = f"{self.base_url}/referentiel/parametres"
        
        params = {
            'format': 'json',
            'size': 5000,
        }
        
        response = self._make_request(url, params)
        data = response.json()
        
        parameters = data.get('data', [])
        
        logger.info(f"📊 {len(parameters)} paramètres disponibles")
        
        return parameters


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def get_bassin_arcachon_connector(config: dict = None) -> HubEauConnector:
    """
    Retourne connecteur configuré pour Bassin d'Arcachon.
    
    Bbox approximative Bassin d'Arcachon:
    - lon_min: -1.30
    - lat_min: 44.60
    - lon_max: -1.15
    - lat_max: 44.75
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Connecteur Hub'Eau
    """
    default_config = {}
    
    if config:
        default_config.update(config)
    
    return HubEauConnector(default_config)


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    # Test recherche stations
    connector = HubEauConnector({})
    
    print("=" * 80)
    print("TEST RECHERCHE STATIONS BASSIN D'ARCACHON")
    print("=" * 80)
    
    # Bbox Bassin d'Arcachon
    bbox = (-1.30, 44.60, -1.15, 44.75)
    
    stations = connector.search_stations(bbox=bbox)
    
    print(f"\n✅ {len(stations)} stations trouvées")
    
    if stations:
        print("\nExemple station:")
        station = stations[0]
        print(f"  Code: {station.get('code_station')}")
        print(f"  Libellé: {station.get('libelle_station')}")
        print(f"  Commune: {station.get('libelle_commune')}")
        print(f"  Coordonnées: ({station.get('longitude')}, {station.get('latitude')})")
    
    # Test récupération données
    if stations:
        print("\n" + "=" * 80)
        print("TEST RÉCUPÉRATION ANALYSES")
        print("=" * 80)
        
        station_codes = [s['code_station'] for s in stations[:3]]  # 3 premières stations
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        
        try:
            measurements = connector.fetch_data(
                start_time,
                end_time,
                station_codes=station_codes
            )
            
            print(f"\n✅ {len(measurements)} mesures récupérées")
            
            if measurements:
                print("\nExemple mesure:")
                m = measurements[0]
                print(f"  Station: {m['station_id']}")
                print(f"  Variable: {m['variable']}")
                print(f"  Valeur: {m['raw_value']} {m['raw_unit']}")
                print(f"  Date: {m['timestamp_utc']}")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
