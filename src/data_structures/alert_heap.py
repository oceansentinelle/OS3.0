"""
Module de Triage des Alertes - Min-Heap
Conformité ABACODE 2.0

Complexité:
    - insert: O(log n)
    - extract_min: O(log n)
    - peek: O(1)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import IntEnum


class AlertPriority(IntEnum):
    """Niveaux de priorité (plus petit = plus urgent)"""
    CRITICAL = 1      # Mortalité imminente (pH < 7.6)
    HIGH = 2          # Stress métabolique (pH < 7.7)
    MEDIUM = 3        # Anomalie détectée
    LOW = 4           # Information


@dataclass
class Alert:
    """
    Structure d'une alerte avec métadonnées ABACODE 2.0
    
    Attributes:
        timestamp: Horodatage de l'alerte
        station_id: Identifiant de la station (ex: "BARAG")
        parameter: Paramètre mesuré (ex: "pH", "O2", "temperature")
        value: Valeur mesurée
        threshold: Seuil critique
        priority: Niveau de priorité
        message: Message descriptif
        source: Source de la donnée (ABACODE 2.0)
        method: Méthode de mesure (ABACODE 2.0)
        uncertainty: Marge d'erreur (ABACODE 2.0)
        version: Version du modèle (ABACODE 2.0)
        status: Statut de validité (ABACODE 2.0)
    """
    timestamp: datetime
    station_id: str
    parameter: str
    value: float
    threshold: float
    priority: AlertPriority
    message: str
    
    # Métadonnées ABACODE 2.0
    source: str
    method: str
    uncertainty: float
    version: str
    status: str  # "measured" | "inferred" | "simulated"


class AlertHeap:
    """
    Min-Heap pour le triage des alertes par priorité
    
    L'alerte la plus urgente est toujours à la racine (index 0).
    Utilise un tableau Python pour le stockage.
    """
    
    def __init__(self):
        self.heap: List[Alert] = []
        self.size = 0
    
    def _parent(self, i: int) -> int:
        """Index du parent"""
        return (i - 1) // 2
    
    def _left_child(self, i: int) -> int:
        """Index de l'enfant gauche"""
        return 2 * i + 1
    
    def _right_child(self, i: int) -> int:
        """Index de l'enfant droit"""
        return 2 * i + 2
    
    def _swap(self, i: int, j: int):
        """Échange deux éléments"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _heapify_up(self, i: int):
        """
        Remonter l'élément pour maintenir la propriété du heap
        Complexité: O(log n)
        """
        while i > 0:
            parent = self._parent(i)
            # Comparaison par priorité (plus petit = plus urgent)
            if self.heap[i].priority < self.heap[parent].priority:
                self._swap(i, parent)
                i = parent
            else:
                break
    
    def _heapify_down(self, i: int):
        """
        Descendre l'élément pour maintenir la propriété du heap
        Complexité: O(log n)
        """
        while True:
            smallest = i
            left = self._left_child(i)
            right = self._right_child(i)
            
            if left < self.size and self.heap[left].priority < self.heap[smallest].priority:
                smallest = left
            
            if right < self.size and self.heap[right].priority < self.heap[smallest].priority:
                smallest = right
            
            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break
    
    def insert(self, alert: Alert):
        """
        Insertion d'une alerte - O(log n)
        
        ABACODE 2.0: Validation des métadonnées obligatoires
        
        Args:
            alert: Alerte à insérer
            
        Raises:
            ValueError: Si métadonnées ABACODE incomplètes
        """
        # Validation ABACODE
        if not all([alert.source, alert.method, alert.version, alert.status]):
            raise ValueError("Métadonnées ABACODE 2.0 incomplètes")
        
        if alert.status not in ["measured", "inferred", "simulated"]:
            raise ValueError(f"Statut invalide: {alert.status}")
        
        self.heap.append(alert)
        self.size += 1
        self._heapify_up(self.size - 1)
    
    def extract_min(self) -> Optional[Alert]:
        """
        Extraction de l'alerte la plus urgente - O(log n)
        
        Returns:
            L'alerte la plus urgente, ou None si le heap est vide
        """
        if self.size == 0:
            return None
        
        # La racine contient l'alerte la plus urgente
        min_alert = self.heap[0]
        
        # Remplacer la racine par le dernier élément
        self.heap[0] = self.heap[self.size - 1]
        self.heap.pop()
        self.size -= 1
        
        # Restructurer le heap
        if self.size > 0:
            self._heapify_down(0)
        
        return min_alert
    
    def peek(self) -> Optional[Alert]:
        """
        Consulter l'alerte la plus urgente sans l'extraire - O(1)
        
        Returns:
            L'alerte la plus urgente, ou None si le heap est vide
        """
        return self.heap[0] if self.size > 0 else None
    
    def get_critical_count(self) -> int:
        """Compter les alertes critiques (priorité CRITICAL)"""
        return sum(1 for alert in self.heap if alert.priority == AlertPriority.CRITICAL)
    
    def get_statistics(self) -> dict:
        """Statistiques du heap"""
        if self.size == 0:
            return {
                "size": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        
        stats = {
            "size": self.size,
            "critical": sum(1 for a in self.heap if a.priority == AlertPriority.CRITICAL),
            "high": sum(1 for a in self.heap if a.priority == AlertPriority.HIGH),
            "medium": sum(1 for a in self.heap if a.priority == AlertPriority.MEDIUM),
            "low": sum(1 for a in self.heap if a.priority == AlertPriority.LOW),
            "most_urgent": self.peek().message if self.peek() else None
        }
        
        return stats
    
    def clear(self):
        """Vider le heap"""
        self.heap.clear()
        self.size = 0


if __name__ == "__main__":
    # Test rapide
    print("=== Test AlertHeap ===")
    
    heap = AlertHeap()
    
    # Insertion d'alertes
    alert1 = Alert(
        timestamp=datetime.now(),
        station_id="BARAG",
        parameter="pH",
        value=7.55,
        threshold=7.6,
        priority=AlertPriority.CRITICAL,
        message="Mortalité imminente - pH critique",
        source="IFREMER_BARAG",
        method="sensor_direct",
        uncertainty=0.02,
        version="v3.0.1",
        status="measured"
    )
    
    alert2 = Alert(
        timestamp=datetime.now(),
        station_id="VPS_PROD",
        parameter="temperature",
        value=23.5,
        threshold=22.0,
        priority=AlertPriority.MEDIUM,
        message="Anomalie thermique",
        source="VPS_PROD",
        method="calculated",
        uncertainty=0.5,
        version="v3.0.1",
        status="inferred"
    )
    
    heap.insert(alert1)
    heap.insert(alert2)
    
    print(f"Taille du heap: {heap.size}")
    print(f"Alerte la plus urgente: {heap.peek().message}")
    print(f"Statistiques: {heap.get_statistics()}")
    
    # Extraction
    most_urgent = heap.extract_min()
    print(f"\nAlerte extraite: {most_urgent.message}")
    print(f"Taille après extraction: {heap.size}")
    
    print("\n✓ Test réussi")
