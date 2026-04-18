"""
Structures de Données Avancées - OCÉAN-SENTINELLE
Conformité ABACODE 2.0

Modules:
    - alert_heap: Heap de priorité pour alertes de mortalité
    - vessel_hashtable: Table de hachage pour indexation AIS
    - connectivity_graph: Graphe de connectivité biologique
"""

__version__ = "3.0.1"
__author__ = "Ocean Sentinelle Team"
__abacode_compliant__ = True

from .alert_heap import AlertHeap, Alert, AlertPriority
from .vessel_hashtable import VesselHashTable, Vessel
from .connectivity_graph import BiologicalConnectivityGraph, Basin, LarvalFlow

__all__ = [
    'AlertHeap',
    'Alert',
    'AlertPriority',
    'VesselHashTable',
    'Vessel',
    'BiologicalConnectivityGraph',
    'Basin',
    'LarvalFlow'
]
