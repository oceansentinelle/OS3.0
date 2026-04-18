"""
Indexation AIS - Table de Hachage
Conformité ABACODE 2.0

Complexité:
    - insert: O(1) moyen
    - search: O(1) moyen
    - delete: O(1) moyen
"""

from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import datetime


@dataclass
class Vessel:
    """
    Données d'un navire avec métadonnées ABACODE 2.0
    
    Attributes:
        mmsi: Identifiant unique 9 chiffres (Maritime Mobile Service Identity)
        name: Nom du navire
        vessel_type: Type ("cargo", "fishing", "passenger", etc.)
        length: Longueur en mètres
        beam: Largeur en mètres
        draft: Tirant d'eau en mètres
        last_position: (latitude, longitude)
        last_update: Dernière mise à jour
        source: Source de la donnée (ABACODE 2.0)
        uncertainty_position: Incertitude position en mètres (ABACODE 2.0)
        version: Version du système (ABACODE 2.0)
        status: Statut de validité (ABACODE 2.0)
    """
    mmsi: int
    name: str
    vessel_type: str
    length: float
    beam: float
    draft: float
    last_position: Tuple[float, float]
    last_update: datetime
    
    # Métadonnées ABACODE 2.0
    source: str
    uncertainty_position: float
    version: str
    status: str  # "measured" | "inferred" | "simulated"


class VesselHashTable:
    """
    Table de hachage pour indexation des navires par MMSI
    
    Utilise le chaînage pour gérer les collisions.
    Fonction de hachage: Division modulo avec nombre premier.
    """
    
    def __init__(self, capacity: int = 10007):
        """
        Initialisation avec un nombre premier pour réduire les collisions
        
        Args:
            capacity: Taille de la table (nombre premier recommandé)
                     10007 permet de gérer ~10000 navires avec facteur de charge < 1
        """
        self.capacity = capacity
        self.table: List[List[Vessel]] = [[] for _ in range(capacity)]
        self.size = 0
        self.collision_count = 0
    
    def _hash(self, mmsi: int) -> int:
        """
        Fonction de hachage modulaire
        
        Méthode: Division modulo avec nombre premier
        Complexité: O(1)
        
        Args:
            mmsi: Identifiant MMSI du navire
            
        Returns:
            Index dans la table de hachage
        """
        return mmsi % self.capacity
    
    def insert(self, vessel: Vessel):
        """
        Insertion d'un navire - O(1) moyen
        
        Gestion des collisions par chaînage (liste chaînée).
        Si le MMSI existe déjà, mise à jour des données.
        
        Args:
            vessel: Navire à insérer
            
        Raises:
            ValueError: Si métadonnées ABACODE incomplètes
        """
        # Validation ABACODE
        if not all([vessel.source, vessel.version, vessel.status]):
            raise ValueError("Métadonnées ABACODE 2.0 incomplètes")
        
        if vessel.status not in ["measured", "inferred", "simulated"]:
            raise ValueError(f"Statut invalide: {vessel.status}")
        
        index = self._hash(vessel.mmsi)
        bucket = self.table[index]
        
        # Vérifier si le MMSI existe déjà (mise à jour)
        for i, v in enumerate(bucket):
            if v.mmsi == vessel.mmsi:
                bucket[i] = vessel
                return
        
        # Nouvelle insertion
        if len(bucket) > 0:
            self.collision_count += 1
        
        bucket.append(vessel)
        self.size += 1
    
    def search(self, mmsi: int) -> Optional[Vessel]:
        """
        Recherche d'un navire par MMSI - O(1) moyen
        
        Args:
            mmsi: Identifiant MMSI du navire
            
        Returns:
            Navire trouvé, ou None si non trouvé
        """
        index = self._hash(mmsi)
        bucket = self.table[index]
        
        for vessel in bucket:
            if vessel.mmsi == mmsi:
                return vessel
        
        return None
    
    def delete(self, mmsi: int) -> bool:
        """
        Suppression d'un navire - O(1) moyen
        
        Args:
            mmsi: Identifiant MMSI du navire
            
        Returns:
            True si supprimé, False si non trouvé
        """
        index = self._hash(mmsi)
        bucket = self.table[index]
        
        for i, vessel in enumerate(bucket):
            if vessel.mmsi == mmsi:
                bucket.pop(i)
                self.size -= 1
                if len(bucket) == 0 and self.collision_count > 0:
                    self.collision_count -= 1
                return True
        
        return False
    
    def get_load_factor(self) -> float:
        """
        Calcul du facteur de charge (load factor)
        
        Facteur optimal: < 0.75
        
        Returns:
            Ratio taille / capacité
        """
        return self.size / self.capacity
    
    def get_collision_rate(self) -> float:
        """
        Taux de collisions
        
        Objectif: < 10%
        
        Returns:
            Pourcentage de collisions
        """
        return (self.collision_count / self.size * 100) if self.size > 0 else 0.0
    
    def get_statistics(self) -> dict:
        """
        Statistiques de performance
        
        Returns:
            Dictionnaire avec métriques de performance
        """
        max_chain_length = max(len(bucket) for bucket in self.table)
        avg_chain_length = sum(len(bucket) for bucket in self.table) / self.capacity
        non_empty_buckets = sum(1 for bucket in self.table if len(bucket) > 0)
        
        return {
            "capacity": self.capacity,
            "size": self.size,
            "load_factor": self.get_load_factor(),
            "collision_rate": self.get_collision_rate(),
            "max_chain_length": max_chain_length,
            "avg_chain_length": avg_chain_length,
            "non_empty_buckets": non_empty_buckets,
            "empty_buckets": self.capacity - non_empty_buckets
        }
    
    def get_all_vessels(self) -> List[Vessel]:
        """
        Récupérer tous les navires
        
        Returns:
            Liste de tous les navires indexés
        """
        vessels = []
        for bucket in self.table:
            vessels.extend(bucket)
        return vessels
    
    def clear(self):
        """Vider la table de hachage"""
        self.table = [[] for _ in range(self.capacity)]
        self.size = 0
        self.collision_count = 0


if __name__ == "__main__":
    # Test rapide
    print("=== Test VesselHashTable ===")
    
    ais_index = VesselHashTable()
    
    # Insertion de navires
    vessel1 = Vessel(
        mmsi=228123456,
        name="CHALUTIER ARCACHON",
        vessel_type="fishing",
        length=25.0,
        beam=6.5,
        draft=2.3,
        last_position=(44.6667, -1.1667),
        last_update=datetime.now(),
        source="AIS_LIVE",
        uncertainty_position=10.0,
        version="v3.0.1",
        status="measured"
    )
    
    vessel2 = Vessel(
        mmsi=228654321,
        name="CARGO BORDEAUX",
        vessel_type="cargo",
        length=150.0,
        beam=25.0,
        draft=8.5,
        last_position=(44.7000, -1.2000),
        last_update=datetime.now(),
        source="AIS_LIVE",
        uncertainty_position=15.0,
        version="v3.0.1",
        status="measured"
    )
    
    ais_index.insert(vessel1)
    ais_index.insert(vessel2)
    
    print(f"Navires indexés: {ais_index.size}")
    
    # Recherche
    found = ais_index.search(228123456)
    if found:
        print(f"Navire trouvé: {found.name} ({found.vessel_type})")
    
    # Statistiques
    stats = ais_index.get_statistics()
    print(f"\nStatistiques:")
    print(f"  Facteur de charge: {stats['load_factor']:.4%}")
    print(f"  Taux de collisions: {stats['collision_rate']:.2f}%")
    print(f"  Longueur max chaîne: {stats['max_chain_length']}")
    
    print("\n✓ Test réussi")
