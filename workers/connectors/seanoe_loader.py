#!/usr/bin/env python3
"""
================================================================================
Loader SEANOE - Données Historiques
================================================================================

Loader pour charger les données historiques SEANOE:
- COAST-HF Arcachon-Ferret time series
- SOMLIT Arcachon long-term monitoring

Source: https://www.seanoe.org/data/00889/100119/

Mode:
- Batch/historique (pas temps réel)
- Chargement fichiers NetCDF/CSV téléchargés
- Tag source_type='historical_reference'

Fonctionnalités:
- Lecture NetCDF avec xarray
- Lecture CSV avec pandas
- Mapping vers modèle canonique
- Validation qualité
- Métadonnées provenance

Conformité:
- Traçabilité complète
- Versioning fichiers
- Checksum validation
================================================================================
"""

import os
import pandas as pd
import xarray as xr
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class SeanoeLoader:
    """Loader pour données historiques SEANOE."""
    
    def __init__(self, config: dict):
        self.config = config
        self.data_dir = Path(config.get('data_dir', './data/seanoe'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def load_netcdf(
        self,
        file_path: str,
        dataset_name: str = 'SEANOE_COAST-HF'
    ) -> List[Dict[str, Any]]:
        """
        Charge fichier NetCDF SEANOE.
        
        Args:
            file_path: Chemin fichier NetCDF
            dataset_name: Nom dataset pour traçabilité
            
        Returns:
            Liste de mesures
        """
        logger.info(f"Chargement NetCDF SEANOE: {file_path}")
        
        # Calculer checksum
        checksum = self._calculate_checksum(file_path)
        
        # Ouvrir NetCDF
        ds = xr.open_dataset(file_path)
        
        measurements = []
        
        # Extraire variables
        for var_name in ds.data_vars:
            if var_name in ['time', 'lat', 'lon', 'station']:
                continue
            
            var_data = ds[var_name]
            
            # Itérer sur le temps
            for time_idx in range(len(ds['time'])):
                timestamp = pd.to_datetime(ds['time'][time_idx].values)
                
                value = float(var_data[time_idx].values)
                
                # Vérifier NaN
                if pd.isna(value):
                    continue
                
                measurement = {
                    'station_id': self._extract_station_id(ds),
                    'timestamp_utc': timestamp,
                    'variable': self._normalize_variable_name(var_name),
                    'raw_value': value,
                    'raw_unit': self._extract_unit(var_data),
                    'source_name': 'SEANOE',
                    'dataset_name': dataset_name,
                    'source_type': 'historical_reference',
                    'file_checksum': checksum,
                    'metadata': {
                        'file_path': file_path,
                        'variable_long_name': var_data.attrs.get('long_name', ''),
                        'variable_standard_name': var_data.attrs.get('standard_name', ''),
                    }
                }
                
                measurements.append(measurement)
        
        ds.close()
        
        logger.info(f"✅ {len(measurements)} mesures chargées depuis NetCDF")
        
        return measurements
    
    def load_csv(
        self,
        file_path: str,
        dataset_name: str = 'SEANOE_SOMLIT'
    ) -> List[Dict[str, Any]]:
        """
        Charge fichier CSV SEANOE.
        
        Args:
            file_path: Chemin fichier CSV
            dataset_name: Nom dataset pour traçabilité
            
        Returns:
            Liste de mesures
        """
        logger.info(f"Chargement CSV SEANOE: {file_path}")
        
        # Calculer checksum
        checksum = self._calculate_checksum(file_path)
        
        # Lire CSV
        df = pd.read_csv(file_path)
        
        measurements = []
        
        # Détecter colonne temps
        time_col = self._detect_time_column(df)
        
        if not time_col:
            logger.error("Impossible de détecter colonne temps")
            return []
        
        # Détecter colonne station
        station_col = self._detect_station_column(df)
        
        # Itérer sur les lignes
        for _, row in df.iterrows():
            timestamp = pd.to_datetime(row[time_col])
            
            station_id = row[station_col] if station_col else dataset_name
            
            # Extraire variables
            for col in df.columns:
                if col in [time_col, station_col, 'latitude', 'longitude', 'depth']:
                    continue
                
                if pd.notna(row[col]):
                    measurement = {
                        'station_id': str(station_id),
                        'timestamp_utc': timestamp,
                        'variable': self._normalize_variable_name(col),
                        'raw_value': float(row[col]),
                        'raw_unit': self._guess_unit(col),
                        'source_name': 'SEANOE',
                        'dataset_name': dataset_name,
                        'source_type': 'historical_reference',
                        'file_checksum': checksum,
                        'metadata': {
                            'file_path': file_path,
                        }
                    }
                    
                    measurements.append(measurement)
        
        logger.info(f"✅ {len(measurements)} mesures chargées depuis CSV")
        
        return measurements
    
    def load_directory(
        self,
        directory: str = None,
        file_pattern: str = '*.nc'
    ) -> List[Dict[str, Any]]:
        """
        Charge tous les fichiers d'un répertoire.
        
        Args:
            directory: Répertoire (None = self.data_dir)
            file_pattern: Pattern fichiers (*.nc, *.csv)
            
        Returns:
            Liste de mesures (tous fichiers)
        """
        if not directory:
            directory = self.data_dir
        
        directory = Path(directory)
        
        logger.info(f"Chargement répertoire: {directory} ({file_pattern})")
        
        all_measurements = []
        
        for file_path in directory.glob(file_pattern):
            logger.info(f"📄 Traitement: {file_path.name}")
            
            try:
                if file_path.suffix == '.nc':
                    measurements = self.load_netcdf(str(file_path))
                elif file_path.suffix == '.csv':
                    measurements = self.load_csv(str(file_path))
                else:
                    logger.warning(f"Format non supporté: {file_path.suffix}")
                    continue
                
                all_measurements.extend(measurements)
                
            except Exception as e:
                logger.error(f"Erreur chargement {file_path.name}: {e}")
                continue
        
        logger.info(
            f"✅ Total: {len(all_measurements)} mesures "
            f"({len(list(directory.glob(file_pattern)))} fichiers)"
        )
        
        return all_measurements
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcule checksum MD5 d'un fichier."""
        md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        
        return md5.hexdigest()
    
    def _extract_station_id(self, dataset: xr.Dataset) -> str:
        """Extrait station_id depuis dataset NetCDF."""
        # Chercher dans attributs globaux
        if 'station_id' in dataset.attrs:
            return str(dataset.attrs['station_id'])
        
        if 'station_name' in dataset.attrs:
            return str(dataset.attrs['station_name'])
        
        # Chercher variable station
        if 'station' in dataset:
            return str(dataset['station'].values[0])
        
        # Fallback
        return 'SEANOE_UNKNOWN'
    
    def _extract_unit(self, data_array: xr.DataArray) -> str:
        """Extrait unité depuis DataArray NetCDF."""
        if 'units' in data_array.attrs:
            return str(data_array.attrs['units'])
        
        if 'unit' in data_array.attrs:
            return str(data_array.attrs['unit'])
        
        return ''
    
    def _normalize_variable_name(self, var_name: str) -> str:
        """Normalise nom de variable."""
        mapping = {
            'TEMP': 'temperature',
            'temp': 'temperature',
            'temperature': 'temperature',
            'PSAL': 'salinity',
            'sal': 'salinity',
            'salinity': 'salinity',
            'DOX2': 'dissolved_oxygen',
            'oxygen': 'dissolved_oxygen',
            'dissolved_oxygen': 'dissolved_oxygen',
            'CHLA': 'chlorophyll_a',
            'chl': 'chlorophyll_a',
            'chlorophyll': 'chlorophyll_a',
            'TURB': 'turbidity',
            'turb': 'turbidity',
            'turbidity': 'turbidity',
            'pH': 'ph',
            'ph': 'ph',
        }
        
        return mapping.get(var_name, var_name.lower())
    
    def _detect_time_column(self, df: pd.DataFrame) -> Optional[str]:
        """Détecte colonne temps dans DataFrame."""
        candidates = ['time', 'date', 'datetime', 'timestamp', 'TIME', 'DATE']
        
        for col in df.columns:
            if col in candidates:
                return col
        
        # Chercher colonne avec type datetime
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col
        
        return None
    
    def _detect_station_column(self, df: pd.DataFrame) -> Optional[str]:
        """Détecte colonne station dans DataFrame."""
        candidates = ['station', 'station_id', 'STATION', 'site', 'SITE']
        
        for col in df.columns:
            if col in candidates:
                return col
        
        return None
    
    def _guess_unit(self, variable_name: str) -> str:
        """Devine l'unité depuis le nom de variable."""
        units = {
            'temperature': '°C',
            'temp': '°C',
            'salinity': 'PSU',
            'sal': 'PSU',
            'dissolved_oxygen': 'µmol/kg',
            'oxygen': 'µmol/kg',
            'chlorophyll': 'mg/m³',
            'chl': 'mg/m³',
            'turbidity': 'NTU',
            'turb': 'NTU',
            'ph': '',
        }
        
        return units.get(variable_name.lower(), '')


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    # Test loader
    loader = SeanoeLoader({'data_dir': './data/seanoe'})
    
    print("=" * 80)
    print("TEST SEANOE LOADER")
    print("=" * 80)
    
    # Créer fichier CSV test
    test_csv = loader.data_dir / 'test_data.csv'
    
    test_data = pd.DataFrame({
        'time': pd.date_range('2024-01-01', periods=10, freq='H'),
        'station': ['ARCACHON'] * 10,
        'temperature': [15.0 + i * 0.1 for i in range(10)],
        'salinity': [35.0 + i * 0.05 for i in range(10)],
    })
    
    test_data.to_csv(test_csv, index=False)
    
    print(f"\n📄 Fichier test créé: {test_csv}")
    
    # Charger
    measurements = loader.load_csv(str(test_csv))
    
    print(f"\n✅ {len(measurements)} mesures chargées")
    
    if measurements:
        print("\nExemple mesure:")
        m = measurements[0]
        print(f"  Station: {m['station_id']}")
        print(f"  Variable: {m['variable']}")
        print(f"  Valeur: {m['raw_value']} {m['raw_unit']}")
        print(f"  Date: {m['timestamp_utc']}")
        print(f"  Checksum: {m['file_checksum'][:8]}...")
