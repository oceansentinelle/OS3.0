#!/usr/bin/env python3
"""
================================================================================
Loader SIBA Enki - Données Qualité Eau Bassin d'Arcachon
================================================================================

Loader pour charger les exports de la plateforme SIBA Enki.

Source: https://www.siba-bassin-arcachon.fr/plateforme-dacces-aux-donnees

Mode:
- Semi-automatisé (export manuel depuis plateforme)
- Dépôt fichiers dans data_drop/
- Job de chargement périodique
- Journal explicite de provenance

Fonctionnalités:
- Lecture CSV/Excel exports SIBA
- Mapping vers modèle canonique
- Validation qualité
- Traçabilité complète

Conformité:
- Source type='siba_export'
- Checksum validation
- Métadonnées provenance
================================================================================
"""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)


class SibaEnkiLoader:
    """Loader pour exports SIBA Enki."""
    
    def __init__(self, config: dict):
        self.config = config
        self.data_drop_dir = Path(config.get('data_drop_dir', './data_drop/siba'))
        self.processed_dir = Path(config.get('processed_dir', './data_drop/siba/processed'))
        
        # Créer répertoires
        self.data_drop_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def load_export(
        self,
        file_path: str,
        export_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Charge un export SIBA Enki.
        
        Args:
            file_path: Chemin fichier export
            export_date: Date export (None = date fichier)
            
        Returns:
            Liste de mesures
        """
        file_path = Path(file_path)
        
        logger.info(f"Chargement export SIBA: {file_path.name}")
        
        # Calculer checksum
        checksum = self._calculate_checksum(file_path)
        
        # Vérifier si déjà traité
        if self._is_already_processed(checksum):
            logger.warning(f"⚠️  Export déjà traité (checksum: {checksum[:8]}...)")
            return []
        
        # Date export
        if not export_date:
            export_date = datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Charger selon format
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            logger.error(f"Format non supporté: {file_path.suffix}")
            return []
        
        # Convertir vers mesures
        measurements = self._convert_to_measurements(
            df,
            file_path,
            checksum,
            export_date
        )
        
        # Marquer comme traité
        self._mark_as_processed(file_path, checksum)
        
        logger.info(f"✅ {len(measurements)} mesures chargées depuis export SIBA")
        
        return measurements
    
    def load_data_drop(self) -> List[Dict[str, Any]]:
        """
        Charge tous les exports non traités du data_drop.
        
        Returns:
            Liste de mesures (tous exports)
        """
        logger.info(f"Scan data_drop: {self.data_drop_dir}")
        
        all_measurements = []
        
        # Chercher fichiers CSV et Excel
        patterns = ['*.csv', '*.xlsx', '*.xls']
        
        for pattern in patterns:
            for file_path in self.data_drop_dir.glob(pattern):
                # Ignorer fichiers processed
                if 'processed' in str(file_path):
                    continue
                
                logger.info(f"📄 Traitement: {file_path.name}")
                
                try:
                    measurements = self.load_export(str(file_path))
                    all_measurements.extend(measurements)
                except Exception as e:
                    logger.error(f"Erreur chargement {file_path.name}: {e}")
                    continue
        
        logger.info(
            f"✅ Total data_drop: {len(all_measurements)} mesures "
            f"(nouveaux exports)"
        )
        
        return all_measurements
    
    def _convert_to_measurements(
        self,
        df: pd.DataFrame,
        file_path: Path,
        checksum: str,
        export_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Convertit DataFrame export SIBA vers modèle canonique.
        
        Format attendu SIBA (à adapter selon export réel):
        - Date/Heure
        - Station/Point de mesure
        - Paramètre
        - Valeur
        - Unité
        """
        measurements = []
        
        # Détecter colonnes
        time_col = self._detect_column(df, ['date', 'datetime', 'heure', 'time'])
        station_col = self._detect_column(df, ['station', 'point', 'site'])
        param_col = self._detect_column(df, ['parametre', 'parameter', 'variable'])
        value_col = self._detect_column(df, ['valeur', 'value', 'resultat'])
        unit_col = self._detect_column(df, ['unite', 'unit', 'unité'])
        
        if not all([time_col, value_col]):
            logger.error("Colonnes obligatoires manquantes (time, value)")
            return []
        
        # Itérer sur les lignes
        for _, row in df.iterrows():
            try:
                timestamp = pd.to_datetime(row[time_col])
                
                station_id = row[station_col] if station_col else 'SIBA_UNKNOWN'
                
                variable = row[param_col] if param_col else 'unknown'
                variable = self._normalize_variable_name(variable)
                
                value = float(row[value_col])
                
                unit = row[unit_col] if unit_col else ''
                
                measurement = {
                    'station_id': str(station_id),
                    'timestamp_utc': timestamp,
                    'variable': variable,
                    'raw_value': value,
                    'raw_unit': str(unit),
                    'source_name': 'SIBA_Enki',
                    'source_type': 'siba_export',
                    'file_checksum': checksum,
                    'metadata': {
                        'file_path': str(file_path),
                        'export_date': export_date.isoformat(),
                        'original_parameter': row[param_col] if param_col else '',
                    }
                }
                
                measurements.append(measurement)
                
            except Exception as e:
                logger.warning(f"Erreur ligne: {e}")
                continue
        
        return measurements
    
    def _detect_column(
        self,
        df: pd.DataFrame,
        candidates: List[str]
    ) -> Optional[str]:
        """Détecte colonne dans DataFrame (case-insensitive)."""
        df_cols_lower = {col.lower(): col for col in df.columns}
        
        for candidate in candidates:
            if candidate.lower() in df_cols_lower:
                return df_cols_lower[candidate.lower()]
        
        return None
    
    def _normalize_variable_name(self, var_name: str) -> str:
        """Normalise nom de variable SIBA."""
        var_lower = str(var_name).lower()
        
        mapping = {
            'température': 'temperature',
            'temperature': 'temperature',
            'temp': 'temperature',
            'salinité': 'salinity',
            'salinity': 'salinity',
            'sal': 'salinity',
            'ph': 'ph',
            'oxygène': 'dissolved_oxygen',
            'oxygene': 'dissolved_oxygen',
            'oxygen': 'dissolved_oxygen',
            'o2': 'dissolved_oxygen',
            'turbidité': 'turbidity',
            'turbidite': 'turbidity',
            'turbidity': 'turbidity',
            'chlorophylle': 'chlorophyll_a',
            'chlorophyll': 'chlorophyll_a',
            'nitrate': 'nitrate',
            'phosphate': 'phosphate',
        }
        
        for key, value in mapping.items():
            if key in var_lower:
                return value
        
        return var_lower.replace(' ', '_')
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcule checksum MD5 d'un fichier."""
        md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        
        return md5.hexdigest()
    
    def _is_already_processed(self, checksum: str) -> bool:
        """Vérifie si un fichier a déjà été traité."""
        processed_file = self.processed_dir / f"{checksum}.processed"
        return processed_file.exists()
    
    def _mark_as_processed(self, file_path: Path, checksum: str):
        """Marque un fichier comme traité."""
        # Créer fichier marqueur
        processed_file = self.processed_dir / f"{checksum}.processed"
        
        with open(processed_file, 'w') as f:
            f.write(f"file: {file_path.name}\n")
            f.write(f"checksum: {checksum}\n")
            f.write(f"processed_at: {datetime.utcnow().isoformat()}\n")
        
        # Déplacer fichier original vers processed/
        try:
            dest = self.processed_dir / file_path.name
            file_path.rename(dest)
            logger.info(f"📦 Fichier déplacé vers processed/")
        except Exception as e:
            logger.warning(f"Impossible de déplacer fichier: {e}")


# ============================================================================
# Tests
# ============================================================================

if __name__ == "__main__":
    # Test loader
    loader = SibaEnkiLoader({
        'data_drop_dir': './data_drop/siba',
        'processed_dir': './data_drop/siba/processed'
    })
    
    print("=" * 80)
    print("TEST SIBA ENKI LOADER")
    print("=" * 80)
    
    # Créer fichier CSV test
    test_csv = loader.data_drop_dir / 'export_siba_test.csv'
    
    test_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10, freq='D'),
        'Station': ['Arcachon Port'] * 10,
        'Paramètre': ['Température', 'Salinité'] * 5,
        'Valeur': [15.0 + i * 0.1 for i in range(10)],
        'Unité': ['°C', 'PSU'] * 5,
    })
    
    test_data.to_csv(test_csv, index=False)
    
    print(f"\n📄 Fichier test créé: {test_csv}")
    
    # Charger data_drop
    measurements = loader.load_data_drop()
    
    print(f"\n✅ {len(measurements)} mesures chargées")
    
    if measurements:
        print("\nExemple mesure:")
        m = measurements[0]
        print(f"  Station: {m['station_id']}")
        print(f"  Variable: {m['variable']}")
        print(f"  Valeur: {m['raw_value']} {m['raw_unit']}")
        print(f"  Date: {m['timestamp_utc']}")
        print(f"  Checksum: {m['file_checksum'][:8]}...")
