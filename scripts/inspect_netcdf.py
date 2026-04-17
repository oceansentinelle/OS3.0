#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel V3.0 - Script d'Inspection NetCDF
=================================================
Outil d'inspection rapide pour fichiers NetCDF COAST-HF

Usage:
    python inspect_netcdf.py fichier.nc
    python inspect_netcdf.py fichier.nc --detailed
    python inspect_netcdf.py fichier.nc --export-csv

Auteur: Ocean Sentinel Team
Date: 2026-04-16
"""

import sys
import argparse
from pathlib import Path
import json

try:
    import xarray as xr
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f"❌ Erreur: {e}")
    print("Installation requise: pip install xarray pandas numpy netCDF4")
    sys.exit(1)


def format_size(bytes_size):
    """Formate une taille en octets en format lisible."""
    for unit in ['o', 'Ko', 'Mo', 'Go']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} To"


def inspect_netcdf(filepath, detailed=False):
    """
    Inspecte un fichier NetCDF et affiche les informations clés.
    
    Args:
        filepath: Chemin vers le fichier NetCDF
        detailed: Si True, affiche des informations détaillées
    """
    
    print("=" * 80)
    print(f"📄 INSPECTION FICHIER NETCDF")
    print("=" * 80)
    print(f"Fichier: {filepath}")
    print()
    
    # Ouverture du fichier
    try:
        ds = xr.open_dataset(filepath)
    except Exception as e:
        print(f"❌ Erreur d'ouverture: {e}")
        return None
    
    # ========================================================================
    # MÉTADONNÉES GLOBALES
    # ========================================================================
    print("🏷️  MÉTADONNÉES GLOBALES")
    print("-" * 80)
    
    important_attrs = [
        'title', 'institution', 'source', 'station_id', 
        'Conventions', 'license', 'time_coverage_start', 
        'time_coverage_end', 'geospatial_lat_min', 'geospatial_lon_min'
    ]
    
    for key in important_attrs:
        if key in ds.attrs:
            print(f"  • {key:25s}: {ds.attrs[key]}")
    
    if detailed:
        print("\n  Autres attributs:")
        for key, value in ds.attrs.items():
            if key not in important_attrs:
                print(f"    - {key}: {value}")
    
    # ========================================================================
    # DIMENSIONS
    # ========================================================================
    print("\n📐 DIMENSIONS")
    print("-" * 80)
    
    for dim, size in ds.dims.items():
        unlimited = " (UNLIMITED)" if size == 0 or dim == 'time' else ""
        print(f"  • {dim:15s}: {size:8d}{unlimited}")
    
    # ========================================================================
    # COORDONNÉES
    # ========================================================================
    print("\n🌍 COORDONNÉES")
    print("-" * 80)
    
    if 'latitude' in ds.coords or 'lat' in ds.coords:
        lat_var = 'latitude' if 'latitude' in ds.coords else 'lat'
        lat_val = float(ds[lat_var].values.flat[0])
        print(f"  • Latitude:  {lat_val:.4f}°N")
    
    if 'longitude' in ds.coords or 'lon' in ds.coords:
        lon_var = 'longitude' if 'longitude' in ds.coords else 'lon'
        lon_val = float(ds[lon_var].values.flat[0])
        print(f"  • Longitude: {lon_val:.4f}°E")
    
    if 'depth' in ds.coords:
        depth_val = float(ds['depth'].values.flat[0])
        print(f"  • Profondeur: {depth_val:.1f} m")
    
    # ========================================================================
    # PLAGE TEMPORELLE
    # ========================================================================
    if 'time' in ds.dims or 'TIME' in ds.dims:
        time_var = 'time' if 'time' in ds.dims else 'TIME'
        
        print("\n⏰ PLAGE TEMPORELLE")
        print("-" * 80)
        
        time_data = ds[time_var]
        
        if len(time_data) > 0:
            time_start = pd.Timestamp(time_data.values[0])
            time_end = pd.Timestamp(time_data.values[-1])
            duration = time_end - time_start
            
            print(f"  • Début:     {time_start}")
            print(f"  • Fin:       {time_end}")
            print(f"  • Durée:     {duration}")
            print(f"  • Points:    {len(time_data):,}")
            
            # Fréquence d'échantillonnage
            if len(time_data) > 1:
                dt = pd.Timestamp(time_data.values[1]) - pd.Timestamp(time_data.values[0])
                freq_minutes = dt.total_seconds() / 60
                print(f"  • Intervalle: {dt} ({freq_minutes:.1f} min)")
                
                # Estimation du taux d'échantillonnage
                samples_per_day = 24 * 60 / freq_minutes
                print(f"  • Fréquence: {samples_per_day:.1f} échantillons/jour")
    
    # ========================================================================
    # VARIABLES
    # ========================================================================
    print("\n📊 VARIABLES DE DONNÉES")
    print("-" * 80)
    
    for var_name in ds.data_vars:
        var_data = ds[var_name]
        
        # Informations de base
        long_name = var_data.attrs.get('long_name', 'N/A')
        units = var_data.attrs.get('units', 'N/A')
        shape = var_data.shape
        dtype = var_data.dtype
        
        print(f"\n  📌 {var_name}")
        print(f"     Nom long: {long_name}")
        print(f"     Unité:    {units}")
        print(f"     Shape:    {shape}")
        print(f"     Type:     {dtype}")
        
        # Statistiques (si données numériques)
        if var_data.size > 0 and np.issubdtype(var_data.dtype, np.number):
            try:
                # Charger un échantillon pour les stats
                sample = var_data.values.flatten()
                sample_clean = sample[~np.isnan(sample)]
                
                if len(sample_clean) > 0:
                    print(f"     Min:      {np.min(sample_clean):.4f}")
                    print(f"     Max:      {np.max(sample_clean):.4f}")
                    print(f"     Moyenne:  {np.mean(sample_clean):.4f}")
                    print(f"     Écart-type: {np.std(sample_clean):.4f}")
                    
                    # Pourcentage de valeurs manquantes
                    missing_pct = (len(sample) - len(sample_clean)) / len(sample) * 100
                    if missing_pct > 0:
                        print(f"     Manquant: {missing_pct:.1f}%")
            except Exception as e:
                print(f"     (Impossible de calculer les stats: {e})")
        
        # Attributs détaillés
        if detailed:
            print("     Attributs:")
            for attr_key, attr_val in var_data.attrs.items():
                if attr_key not in ['long_name', 'units']:
                    print(f"       - {attr_key}: {attr_val}")
    
    # ========================================================================
    # TAILLE DU FICHIER
    # ========================================================================
    print("\n💾 INFORMATIONS FICHIER")
    print("-" * 80)
    
    import os
    file_size = os.path.getsize(filepath)
    print(f"  • Taille: {format_size(file_size)}")
    
    # Estimation mémoire chargement complet
    total_elements = sum(var.size for var in ds.data_vars.values())
    estimated_memory = total_elements * 8  # Assume float64
    print(f"  • Mémoire estimée (chargement complet): {format_size(estimated_memory)}")
    
    # ========================================================================
    # RECOMMANDATIONS
    # ========================================================================
    print("\n💡 RECOMMANDATIONS INGESTION")
    print("-" * 80)
    
    if 'time' in ds.dims:
        n_time = len(ds.time)
        
        # Calcul chunk size optimal
        if estimated_memory > 256 * 1024 * 1024:  # > 256 Mo
            recommended_chunk = max(100, n_time // (estimated_memory // (256 * 1024 * 1024)))
            print(f"  ⚠️  Fichier volumineux détecté!")
            print(f"  • Utiliser: --chunk-size-netcdf {recommended_chunk}")
            print(f"  • Commande suggérée:")
            print(f"    python scripts/ingestion_stream.py {filepath.name} \\")
            print(f"      --format netcdf --chunk-size-netcdf {recommended_chunk}")
        else:
            print(f"  ✓ Taille acceptable pour ingestion standard")
            print(f"  • Commande suggérée:")
            print(f"    python scripts/ingestion_stream.py {filepath.name} --format netcdf")
    
    # Vérification compatibilité COAST-HF
    print("\n🔍 COMPATIBILITÉ COAST-HF")
    print("-" * 80)
    
    coast_hf_vars = ['TEMP', 'PSAL', 'DOX2', 'PH_TOTAL', 'ATMS', 'WSPD', 'WDIR']
    found_vars = [v for v in coast_hf_vars if v in ds.data_vars]
    
    if found_vars:
        print(f"  ✓ Variables COAST-HF détectées: {', '.join(found_vars)}")
    else:
        print(f"  ⚠️  Aucune variable COAST-HF standard détectée")
        print(f"  • Variables présentes: {', '.join(list(ds.data_vars)[:5])}")
    
    # Vérification CF compliance
    if 'Conventions' in ds.attrs:
        conventions = ds.attrs['Conventions']
        if 'CF' in conventions:
            print(f"  ✓ Conforme CF: {conventions}")
        else:
            print(f"  ⚠️  Convention: {conventions} (non-CF)")
    
    ds.close()
    
    print("\n" + "=" * 80)
    print("✅ Inspection terminée")
    print("=" * 80)
    
    return ds


def export_to_csv(filepath, output_csv=None):
    """
    Exporte un fichier NetCDF en CSV.
    
    Args:
        filepath: Chemin vers le fichier NetCDF
        output_csv: Chemin du fichier CSV de sortie (optionnel)
    """
    if output_csv is None:
        output_csv = filepath.with_suffix('.csv')
    
    print(f"📤 Export CSV: {filepath} → {output_csv}")
    
    ds = xr.open_dataset(filepath)
    df = ds.to_dataframe()
    df.to_csv(output_csv)
    
    print(f"✓ Export terminé: {len(df)} lignes")
    print(f"  Colonnes: {', '.join(df.columns)}")
    
    ds.close()


def export_metadata_json(filepath, output_json=None):
    """
    Exporte les métadonnées en JSON.
    
    Args:
        filepath: Chemin vers le fichier NetCDF
        output_json: Chemin du fichier JSON de sortie (optionnel)
    """
    if output_json is None:
        output_json = filepath.with_suffix('.metadata.json')
    
    print(f"📤 Export métadonnées JSON: {output_json}")
    
    ds = xr.open_dataset(filepath)
    
    metadata = {
        'global_attributes': dict(ds.attrs),
        'dimensions': {k: int(v) for k, v in ds.dims.items()},
        'variables': {}
    }
    
    for var_name in ds.data_vars:
        var_data = ds[var_name]
        metadata['variables'][var_name] = {
            'attributes': dict(var_data.attrs),
            'shape': list(var_data.shape),
            'dtype': str(var_data.dtype)
        }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Métadonnées exportées")
    
    ds.close()


def main():
    """Point d'entrée CLI."""
    parser = argparse.ArgumentParser(
        description='Ocean Sentinel V3.0 - Inspection de fichiers NetCDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s fichier.nc
  %(prog)s fichier.nc --detailed
  %(prog)s fichier.nc --export-csv
  %(prog)s fichier.nc --export-metadata
        """
    )
    
    parser.add_argument('file', type=Path, help='Fichier NetCDF à inspecter')
    parser.add_argument('--detailed', '-d', action='store_true', help='Affichage détaillé')
    parser.add_argument('--export-csv', action='store_true', help='Exporter en CSV')
    parser.add_argument('--export-metadata', action='store_true', help='Exporter métadonnées JSON')
    parser.add_argument('--output', '-o', type=Path, help='Fichier de sortie (CSV ou JSON)')
    
    args = parser.parse_args()
    
    # Vérification fichier
    if not args.file.exists():
        print(f"❌ Fichier introuvable: {args.file}")
        sys.exit(1)
    
    # Inspection
    inspect_netcdf(args.file, detailed=args.detailed)
    
    # Exports optionnels
    if args.export_csv:
        export_to_csv(args.file, args.output)
    
    if args.export_metadata:
        export_metadata_json(args.file, args.output)


if __name__ == '__main__':
    main()
