#!/usr/bin/env python3
"""
================================================================================
Connecteur ERDDAP Ifremer
================================================================================

Connecteur pour récupérer les données océanographiques depuis ERDDAP Ifremer.

Sources:
- https://erddap.ifremer.fr/erddap/tabledap/
- COAST-HF Arcachon-Ferret
- SOMLIT Arcachon

Fonctionnalités:
- Découverte datasets
- Requêtes tabledap avec filtres temporels/spatiaux
- Parsing CSV/JSON
- Mapping vers modèle canonique
- Watermark par dataset/station

Conformité:
- Collecte incrémentale
- Retry avec backoff
- Timeout 30s
- Logging structuré
================================================================================
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from .base import BaseConnector

logger = logging.getLogger(__name__)


class ErddapIfremerConnector(BaseConnector):
    """Connecteur ERDDAP Ifremer."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://erddap.ifremer.fr/erddap')
        self.dataset_id = config.get('dataset_id', 'COAST-HF_Arcachon')
        
    def fetch_data(
        self,
        start_time: datetime,
        end_time: datetime,
        variables: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère données ERDDAP tabledap.
        
        Args:
            start_time: Début période
            end_time: Fin période
            variables: Liste variables à récupérer (None = toutes)
            
        Returns:
            Liste de mesures
        """
        logger.info(
            f"Récupération ERDDAP Ifremer: {self.dataset_id} "
            f"[{start_time.isoformat()} - {end_time.isoformat()}]"
        )
        
        # Construire URL tabledap
        url = f"{self.base_url}/tabledap/{self.dataset_id}.csv"
        
        # Paramètres de requête
        params = {
            'time>=': start_time.isoformat() + 'Z',
            'time<=': end_time.isoformat() + 'Z',
        }
        
        # Variables spécifiques si demandées
        if variables:
            params['variables'] = ','.join(variables)
        
        # Requête HTTP
        response = self._make_request(url, params)
        
        # Parser CSV
        measurements = self._parse_csv_response(response.text)
        
        logger.info(f"✅ {len(measurements)} mesures récupérées")
        
        return measurements
    
    def _parse_csv_response(self, csv_text: str) -> List[Dict[str, Any]]:
        """
        Parse réponse CSV ERDDAP.
        
        ERDDAP retourne:
        - Ligne 1: noms colonnes
        - Ligne 2: unités
        - Lignes 3+: données
        """
        from io import StringIO
        
        # Lire CSV en sautant la ligne des unités
        df = pd.read_csv(StringIO(csv_text), skiprows=[1])
        
        measurements = []
        
        for _, row in df.iterrows():
            # Mapping ERDDAP → modèle canonique
            measurement = {
                'station_id': self._extract_station_id(row),
                'timestamp_utc': pd.to_datetime(row['time']),
                'source_name': 'ERDDAP_Ifremer',
                'dataset_id': self.dataset_id,
            }
            
            # Extraire variables
            for col in df.columns:
                if col in ['time', 'station', 'latitude', 'longitude']:
                    continue
                
                if pd.notna(row[col]):
                    measurements.append({
                        **measurement,
                        'variable': self._normalize_variable_name(col),
                        'raw_value': float(row[col]),
                        'raw_unit': self._get_unit_for_variable(col),
                    })
        
        return measurements
    
    def _extract_station_id(self, row: pd.Series) -> str:
        """Extrait station_id depuis la ligne."""
        # ERDDAP peut avoir 'station' ou 'station_id'
        if 'station' in row:
            return str(row['station'])
        elif 'station_id' in row:
            return str(row['station_id'])
        else:
            return self.dataset_id
    
    def _normalize_variable_name(self, erddap_name: str) -> str:
        """
        Normalise nom de variable ERDDAP vers nom canonique.
        
        Exemples:
        - TEMP → temperature
        - PSAL → salinity
        - DOX2 → dissolved_oxygen
        """
        mapping = {
            'TEMP': 'temperature',
            'temperature': 'temperature',
            'PSAL': 'salinity',
            'salinity': 'salinity',
            'DOX2': 'dissolved_oxygen',
            'dissolved_oxygen': 'dissolved_oxygen',
            'CHLA': 'chlorophyll_a',
            'chlorophyll': 'chlorophyll_a',
            'TURB': 'turbidity',
            'turbidity': 'turbidity',
            'pH': 'ph',
            'ph': 'ph',
        }
        
        return mapping.get(erddap_name, erddap_name.lower())
    
    def _get_unit_for_variable(self, variable: str) -> str:
        """
        Retourne l'unité attendue pour une variable ERDDAP.
        
        Note: ERDDAP fournit les unités en ligne 2 du CSV,
        mais on peut aussi avoir une table de référence.
        """
        units = {
            'TEMP': '°C',
            'temperature': '°C',
            'PSAL': 'PSU',
            'salinity': 'PSU',
            'DOX2': 'µmol/kg',
            'dissolved_oxygen': 'µmol/kg',
            'CHLA': 'mg/m³',
            'chlorophyll': 'mg/m³',
            'TURB': 'NTU',
            'turbidity': 'NTU',
            'pH': '',
            'ph': '',
        }
        
        return units.get(variable, '')
    
    def discover_datasets(self, search_term: str = 'Arcachon') -> List[Dict[str, Any]]:
        """
        Découvre les datasets ERDDAP disponibles.
        
        Args:
            search_term: Terme de recherche
            
        Returns:
            Liste de datasets
        """
        url = f"{self.base_url}/tabledap/allDatasets.csv"
        
        params = {
            'datasetID~': search_term,
        }
        
        response = self._make_request(url, params)
        
        # Parser CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text), skiprows=[1])
        
        datasets = []
        for _, row in df.iterrows():
            datasets.append({
                'dataset_id': row['datasetID'],
                'title': row.get('title', ''),
                'summary': row.get('summary', ''),
                'institution': row.get('institution', ''),
            })
        
        logger.info(f"📊 {len(datasets)} datasets trouvés pour '{search_term}'")
        
        return datasets
    
    def get_dataset_metadata(self, dataset_id: str = None) -> Dict[str, Any]:
        """
        Récupère métadonnées d'un dataset.
        
        Args:
            dataset_id: ID dataset (None = utiliser self.dataset_id)
            
        Returns:
            Métadonnées
        """
        if not dataset_id:
            dataset_id = self.dataset_id
        
        url = f"{self.base_url}/tabledap/{dataset_id}.das"
        
        response = self._make_request(url)
        
        # Parser DAS (Dataset Attribute Structure)
        # Format texte structuré
        metadata = {
            'dataset_id': dataset_id,
            'raw_das': response.text,
        }
        
        # TODO: Parser DAS proprement si besoin
        
        return metadata


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def get_coast_hf_arcachon_connector(config: dict = None) -> ErddapIfremerConnector:
    """
    Retourne connecteur configuré pour COAST-HF Arcachon-Ferret.
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Connecteur ERDDAP
    """
    default_config = {
        'base_url': 'https://erddap.ifremer.fr/erddap',
        'dataset_id': 'COAST-HF_Arcachon_Ferret',
    }
    
    if config:
        default_config.update(config)
    
    return ErddapIfremerConnector(default_config)


def get_somlit_arcachon_connector(config: dict = None) -> ErddapIfremerConnector:
    """
    Retourne connecteur configuré pour SOMLIT Arcachon.
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Connecteur ERDDAP
    """
    default_config = {
        'base_url': 'https://erddap.ifremer.fr/erddap',
        'dataset_id': 'SOMLIT_Arcachon',
    }
    
    if config:
        default_config.update(config)
    
    return ErddapIfremerConnector(default_config)


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    # Test découverte datasets
    connector = ErddapIfremerConnector({})
    
    print("=" * 80)
    print("TEST DÉCOUVERTE DATASETS ARCACHON")
    print("=" * 80)
    
    datasets = connector.discover_datasets('Arcachon')
    
    for ds in datasets:
        print(f"\n📊 {ds['dataset_id']}")
        print(f"   Titre: {ds['title']}")
        print(f"   Institution: {ds['institution']}")
    
    # Test récupération données
    if datasets:
        print("\n" + "=" * 80)
        print("TEST RÉCUPÉRATION DONNÉES")
        print("=" * 80)
        
        connector.dataset_id = datasets[0]['dataset_id']
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        
        try:
            measurements = connector.fetch_data(start_time, end_time)
            
            print(f"\n✅ {len(measurements)} mesures récupérées")
            
            if measurements:
                print("\nExemple mesure:")
                print(measurements[0])
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
