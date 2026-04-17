#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ocean Sentinel V3.0 - Agent IA & Scientifique
==============================================
Pipeline de Machine Learning pour prédiction et détection d'anomalies.

Modèles implémentés:
- LSTM (Long Short-Term Memory) pour prédiction de séries temporelles
- Isolation Forest pour détection d'anomalies océanographiques

Formules scientifiques UNESCO/IOC:
- Salinité Pratique (PSS-78)
- Oxygène dissous (Garcia & Gordon, 1992)

Auteur: Ocean Sentinel Team - Agent IA & Scientifique
Date: 2026-04-16
Licence: Projet ILICO - Infrastructure de Recherche
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any, Optional, List
import numpy as np
import pandas as pd

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FORMULES SCIENTIFIQUES UNESCO/IOC
# ============================================================================

class OceanographicFormulas:
    """
    Implémentation des formules océanographiques standardisées.
    Références: UNESCO, IOC, Garcia & Gordon (1992)
    """
    
    @staticmethod
    def practical_salinity_pss78(conductivity_ratio: float, temperature: float, pressure: float) -> float:
        """
        Calcule la salinité pratique selon PSS-78 (UNESCO).
        
        Référence: Practical Salinity Scale 1978 (PSS-78)
        UNESCO Technical Papers in Marine Science No. 37, 1981
        
        Args:
            conductivity_ratio: Rapport C(S,t,p)/C(35,15,0)
            temperature: Température in situ (°C)
            pressure: Pression (dbar)
            
        Returns:
            Salinité pratique (PSU)
        """
        R = conductivity_ratio
        t = temperature
        p = pressure
        
        # Coefficients PSS-78
        a0 = 0.0080
        a1 = -0.1692
        a2 = 25.3851
        a3 = 14.0941
        a4 = -7.0261
        a5 = 2.7081
        
        b0 = 0.0005
        b1 = -0.0056
        b2 = -0.0066
        b3 = -0.0375
        b4 = 0.0636
        b5 = -0.0144
        
        k = 0.0162
        
        # Calcul de Rt (correction température)
        c0 = 0.6766097
        c1 = 2.00564e-2
        c2 = 1.104259e-4
        c3 = -6.9698e-7
        c4 = 1.0031e-9
        
        Rt = c0 + c1*t + c2*t**2 + c3*t**3 + c4*t**4
        
        # Calcul de Rp (correction pression)
        d1 = 3.426e-2
        d2 = 4.464e-4
        d3 = 4.215e-1
        d4 = -3.107e-3
        
        e1 = 2.070e-5
        e2 = -6.370e-10
        e3 = 3.989e-15
        
        Rp = 1 + (p*(e1 + e2*p + e3*p**2)) / (1 + d1*t + d2*t**2 + (d3 + d4*t)*R)
        
        # Rapport corrigé
        RT = R / (Rp * Rt)
        
        # Salinité
        sqrt_RT = np.sqrt(RT)
        
        S = (a0 + a1*sqrt_RT + a2*RT + a3*RT*sqrt_RT + a4*RT**2 + a5*RT**2*sqrt_RT) + \
            (t - 15) / (1 + k*(t - 15)) * \
            (b0 + b1*sqrt_RT + b2*RT + b3*RT*sqrt_RT + b4*RT**2 + b5*RT**2*sqrt_RT)
        
        return float(S)
    
    @staticmethod
    def dissolved_oxygen_garcia_gordon(temperature: float, salinity: float, pressure: float = 0) -> float:
        """
        Calcule la concentration d'oxygène dissous à saturation.
        
        Référence: Garcia & Gordon (1992) - Oxygen solubility in seawater:
        Better fitting equations. Limnology and Oceanography, 37(6), 1307-1312.
        
        Args:
            temperature: Température (°C)
            salinity: Salinité (PSU)
            pressure: Pression (dbar, optionnel)
            
        Returns:
            Concentration O2 à saturation (µmol/kg)
        """
        T = temperature
        S = salinity
        
        # Conversion température en échelle absolue réduite
        Ts = np.log((298.15 - T) / (273.15 + T))
        
        # Coefficients Garcia & Gordon (1992)
        A0 = 5.80871
        A1 = 3.20291
        A2 = 4.17887
        A3 = 5.10006
        A4 = -9.86643e-2
        A5 = 3.80369
        
        B0 = -7.01577e-3
        B1 = -7.70028e-3
        B2 = -1.13864e-2
        B3 = -9.51519e-3
        
        C0 = -2.75915e-7
        
        # Calcul de la concentration (ml/L)
        ln_C = A0 + A1*Ts + A2*Ts**2 + A3*Ts**3 + A4*Ts**4 + A5*Ts**5 + \
               S * (B0 + B1*Ts + B2*Ts**2 + B3*Ts**3) + \
               C0 * S**2
        
        C_ml_L = np.exp(ln_C)
        
        # Conversion ml/L -> µmol/kg
        # Densité de l'eau de mer ~ 1.025 kg/L
        # 1 ml O2 = 44.66 µmol
        C_umol_kg = C_ml_L * 44.66 / 1.025
        
        # Correction pression (effet hydrostatique)
        if pressure > 0:
            # Correction simplifiée (effet mineur)
            C_umol_kg *= (1 + pressure * 0.000045)
        
        return float(C_umol_kg)
    
    @staticmethod
    def oxygen_saturation_percent(measured_o2: float, temperature: float, salinity: float) -> float:
        """
        Calcule le pourcentage de saturation en oxygène.
        
        Args:
            measured_o2: O2 mesuré (µmol/kg)
            temperature: Température (°C)
            salinity: Salinité (PSU)
            
        Returns:
            Saturation en O2 (%)
        """
        o2_sat = OceanographicFormulas.dissolved_oxygen_garcia_gordon(temperature, salinity)
        return (measured_o2 / o2_sat) * 100 if o2_sat > 0 else 0


# ============================================================================
# MODÈLE LSTM POUR PRÉDICTION DE SÉRIES TEMPORELLES
# ============================================================================

class LSTMPredictor:
    """
    Modèle LSTM pour prédiction de paramètres océanographiques.
    Architecture: Bidirectional LSTM + Dropout + Dense
    """
    
    def __init__(self, sequence_length: int = 24, n_features: int = 5, n_units: int = 64):
        """
        Initialise le modèle LSTM.
        
        Args:
            sequence_length: Longueur de la séquence d'entrée (ex: 24h)
            n_features: Nombre de features (variables)
            n_units: Nombre d'unités LSTM
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.n_units = n_units
        self.model = None
        self.scaler = None
        
        logger.info(f"🧠 Initialisation LSTM: seq={sequence_length}, features={n_features}, units={n_units}")
    
    def build_model(self):
        """Construit l'architecture du modèle LSTM."""
        try:
            from tensorflow import keras
            from tensorflow.keras import layers
        except ImportError:
            logger.error("TensorFlow requis. Installation: pip install tensorflow")
            raise
        
        model = keras.Sequential([
            # Couche LSTM bidirectionnelle
            layers.Bidirectional(
                layers.LSTM(self.n_units, return_sequences=True),
                input_shape=(self.sequence_length, self.n_features)
            ),
            layers.Dropout(0.2),
            
            # Deuxième couche LSTM
            layers.LSTM(self.n_units // 2, return_sequences=False),
            layers.Dropout(0.2),
            
            # Couches denses
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.1),
            layers.Dense(self.n_features)  # Prédiction multi-variables
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        logger.info(f"✓ Modèle LSTM construit: {model.count_params()} paramètres")
        
        return model
    
    def prepare_sequences(self, data: pd.DataFrame, target_columns: List[str]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prépare les séquences pour l'entraînement LSTM.
        
        Args:
            data: DataFrame avec colonnes temporelles
            target_columns: Colonnes à prédire
            
        Returns:
            (X, y) séquences d'entrée et cibles
        """
        from sklearn.preprocessing import StandardScaler
        
        # Normalisation
        self.scaler = StandardScaler()
        data_scaled = self.scaler.fit_transform(data[target_columns])
        
        X, y = [], []
        
        for i in range(len(data_scaled) - self.sequence_length):
            X.append(data_scaled[i:i + self.sequence_length])
            y.append(data_scaled[i + self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None,
              epochs: int = 50, batch_size: int = 32) -> Dict[str, Any]:
        """
        Entraîne le modèle LSTM.
        
        Args:
            X_train: Séquences d'entraînement
            y_train: Cibles d'entraînement
            X_val: Séquences de validation (optionnel)
            y_val: Cibles de validation (optionnel)
            epochs: Nombre d'époques
            batch_size: Taille des batchs
            
        Returns:
            Historique d'entraînement
        """
        if self.model is None:
            self.build_model()
        
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
        ]
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        logger.info(f"🎯 Entraînement LSTM: {epochs} époques, batch={batch_size}")
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("✓ Entraînement terminé")
        
        return history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Prédit les valeurs futures.
        
        Args:
            X: Séquences d'entrée
            
        Returns:
            Prédictions dénormalisées
        """
        if self.model is None:
            raise ValueError("Modèle non entraîné")
        
        predictions_scaled = self.model.predict(X)
        predictions = self.scaler.inverse_transform(predictions_scaled)
        
        return predictions
    
    def save(self, filepath: Path):
        """Sauvegarde le modèle."""
        if self.model is None:
            raise ValueError("Aucun modèle à sauvegarder")
        
        self.model.save(filepath)
        logger.info(f"💾 Modèle sauvegardé: {filepath}")
    
    def load(self, filepath: Path):
        """Charge un modèle sauvegardé."""
        from tensorflow import keras
        
        self.model = keras.models.load_model(filepath)
        logger.info(f"📂 Modèle chargé: {filepath}")


# ============================================================================
# ISOLATION FOREST POUR DÉTECTION D'ANOMALIES
# ============================================================================

class AnomalyDetector:
    """
    Détection d'anomalies océanographiques via Isolation Forest.
    Identifie les événements exceptionnels (hypoxie, bloom algal, etc.)
    """
    
    def __init__(self, contamination: float = 0.05, n_estimators: int = 100):
        """
        Initialise le détecteur d'anomalies.
        
        Args:
            contamination: Proportion attendue d'anomalies (0.05 = 5%)
            n_estimators: Nombre d'arbres dans la forêt
        """
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        logger.info(f"🔍 Initialisation Isolation Forest: contamination={contamination}")
    
    def build_model(self):
        """Construit le modèle Isolation Forest."""
        from sklearn.ensemble import IsolationForest
        
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        
        logger.info(f"✓ Isolation Forest construit: {self.n_estimators} arbres")
        
        return self.model
    
    def fit(self, data: pd.DataFrame, feature_columns: List[str]):
        """
        Entraîne le détecteur sur des données normales.
        
        Args:
            data: DataFrame avec données océanographiques
            feature_columns: Colonnes à utiliser pour la détection
        """
        from sklearn.preprocessing import RobustScaler
        
        if self.model is None:
            self.build_model()
        
        self.feature_names = feature_columns
        
        # Normalisation robuste (résistante aux outliers)
        self.scaler = RobustScaler()
        data_scaled = self.scaler.fit_transform(data[feature_columns])
        
        logger.info(f"🎯 Entraînement Isolation Forest sur {len(data)} échantillons")
        
        self.model.fit(data_scaled)
        
        logger.info("✓ Entraînement terminé")
    
    def detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Détecte les anomalies dans de nouvelles données.
        
        Args:
            data: DataFrame avec données à analyser
            
        Returns:
            DataFrame avec colonnes 'anomaly' (-1=anomalie, 1=normal) et 'anomaly_score'
        """
        if self.model is None:
            raise ValueError("Modèle non entraîné")
        
        data_scaled = self.scaler.transform(data[self.feature_names])
        
        # Prédiction (-1 = anomalie, 1 = normal)
        predictions = self.model.predict(data_scaled)
        
        # Score d'anomalie (plus négatif = plus anormal)
        scores = self.model.score_samples(data_scaled)
        
        result = data.copy()
        result['anomaly'] = predictions
        result['anomaly_score'] = scores
        result['is_anomaly'] = predictions == -1
        
        n_anomalies = (predictions == -1).sum()
        logger.info(f"🚨 {n_anomalies} anomalies détectées ({n_anomalies/len(data)*100:.2f}%)")
        
        return result
    
    def get_anomaly_features(self, anomaly_data: pd.DataFrame) -> Dict[str, float]:
        """
        Analyse les features contribuant aux anomalies.
        
        Args:
            anomaly_data: DataFrame contenant les anomalies
            
        Returns:
            Dict avec statistiques par feature
        """
        stats = {}
        
        for feature in self.feature_names:
            stats[feature] = {
                'mean': float(anomaly_data[feature].mean()),
                'std': float(anomaly_data[feature].std()),
                'min': float(anomaly_data[feature].min()),
                'max': float(anomaly_data[feature].max())
            }
        
        return stats


# ============================================================================
# PIPELINE COMPLET
# ============================================================================

class OceanSentinelMLPipeline:
    """
    Pipeline ML complet pour Ocean Sentinel V3.0.
    Combine prédiction LSTM et détection d'anomalies.
    """
    
    def __init__(self):
        """Initialise le pipeline."""
        self.lstm_predictor = None
        self.anomaly_detector = None
        self.formulas = OceanographicFormulas()
        
        logger.info("🌊 Initialisation Ocean Sentinel ML Pipeline")
    
    def load_data_from_db(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        Charge les données depuis TimescaleDB.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            DataFrame avec données océanographiques
        """
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '6543')),
            database=os.getenv('DB_NAME', 'oceansentinelle'),
            user=os.getenv('DB_USER', 'oceansentinel'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        query = """
            SELECT 
                time, temperature_air, temperature_water, salinity, ph, dissolved_oxygen,
                wind_speed, pressure, humidity
            FROM barag.sensor_data
            WHERE time BETWEEN %s AND %s
            AND quality_flag = 0
            ORDER BY time
        """
        
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        
        logger.info(f"📊 Données chargées: {len(df)} lignes de {start_date} à {end_date}")
        
        return df
    
    def run_prediction_pipeline(self, data: pd.DataFrame, target_columns: List[str]) -> Dict[str, Any]:
        """
        Exécute le pipeline de prédiction LSTM.
        
        Args:
            data: DataFrame avec données historiques
            target_columns: Variables à prédire
            
        Returns:
            Dict avec prédictions et métriques
        """
        logger.info("🔮 Démarrage pipeline de prédiction LSTM")
        
        # Initialisation LSTM
        self.lstm_predictor = LSTMPredictor(
            sequence_length=24,  # 24 heures
            n_features=len(target_columns),
            n_units=64
        )
        
        # Préparation des données
        X, y = self.lstm_predictor.prepare_sequences(data, target_columns)
        
        # Split train/val
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Entraînement
        history = self.lstm_predictor.train(X_train, y_train, X_val, y_val, epochs=50)
        
        # Prédictions
        predictions = self.lstm_predictor.predict(X_val)
        
        return {
            'history': history,
            'predictions': predictions,
            'actual': y_val,
            'target_columns': target_columns
        }
    
    def run_anomaly_detection_pipeline(self, data: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
        """
        Exécute le pipeline de détection d'anomalies.
        
        Args:
            data: DataFrame avec données
            feature_columns: Variables pour la détection
            
        Returns:
            DataFrame avec anomalies détectées
        """
        logger.info("🚨 Démarrage pipeline de détection d'anomalies")
        
        # Initialisation Isolation Forest
        self.anomaly_detector = AnomalyDetector(contamination=0.05)
        
        # Entraînement sur données normales (80% premiers)
        split_idx = int(len(data) * 0.8)
        train_data = data.iloc[:split_idx]
        test_data = data.iloc[split_idx:]
        
        self.anomaly_detector.fit(train_data, feature_columns)
        
        # Détection sur données test
        results = self.anomaly_detector.detect_anomalies(test_data)
        
        # Analyse des anomalies
        anomalies = results[results['is_anomaly']]
        if len(anomalies) > 0:
            logger.warning(f"⚠️ {len(anomalies)} anomalies détectées")
            stats = self.anomaly_detector.get_anomaly_features(anomalies)
            logger.info(f"📊 Statistiques anomalies: {stats}")
        
        return results


# ============================================================================
# CLI
# ============================================================================

def main():
    """Point d'entrée CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ocean Sentinel V3.0 - ML Pipeline')
    parser.add_argument('--mode', choices=['predict', 'detect', 'full'], default='full')
    parser.add_argument('--start-date', type=str, help='Date début (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='Date fin (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Dates par défaut (30 derniers jours)
    end_date = datetime.now() if not args.end_date else datetime.fromisoformat(args.end_date)
    start_date = end_date - timedelta(days=30) if not args.start_date else datetime.fromisoformat(args.start_date)
    
    # Initialisation pipeline
    pipeline = OceanSentinelMLPipeline()
    
    # Chargement données
    data = pipeline.load_data_from_db(start_date, end_date)
    
    if args.mode in ['predict', 'full']:
        target_cols = ['temperature_water', 'salinity', 'ph', 'dissolved_oxygen']
        results = pipeline.run_prediction_pipeline(data, target_cols)
        logger.info(f"✓ Prédictions générées")
    
    if args.mode in ['detect', 'full']:
        feature_cols = ['temperature_water', 'salinity', 'ph', 'dissolved_oxygen', 'wind_speed']
        anomalies = pipeline.run_anomaly_detection_pipeline(data, feature_cols)
        logger.info(f"✓ Détection d'anomalies terminée")


if __name__ == '__main__':
    main()
