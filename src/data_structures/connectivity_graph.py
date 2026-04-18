"""
Connectivité Biologique - Graphe
Conformité ABACODE 2.0

Complexité:
    - add_basin: O(1)
    - add_flow: O(1)
    - dijkstra: O((V + E) log V)
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
import heapq


@dataclass
class Basin:
    """
    Bassin ostréicole avec métadonnées ABACODE 2.0
    
    Attributes:
        id: Identifiant unique (ex: "BARAG")
        name: Nom complet du bassin
        coordinates: (latitude, longitude)
        capacity: Nombre de parcs ostréicoles
        source: Source de la donnée (ABACODE 2.0)
        version: Version du système (ABACODE 2.0)
        status: Statut de validité (ABACODE 2.0)
    """
    id: str
    name: str
    coordinates: Tuple[float, float]
    capacity: int
    
    # Métadonnées ABACODE 2.0
    source: str
    version: str
    status: str  # "measured" | "inferred" | "simulated"


@dataclass
class LarvalFlow:
    """
    Flux larvaire entre deux bassins avec métadonnées ABACODE 2.0
    
    Attributes:
        from_basin: ID du bassin source
        to_basin: ID du bassin destination
        probability: Probabilité de transport (0.0 à 1.0)
        distance_km: Distance physique en kilomètres
        current_speed: Vitesse du courant en m/s
        source: Source de la donnée (ABACODE 2.0)
        method: Méthode de calcul (ABACODE 2.0)
        uncertainty: Incertitude sur la probabilité (ABACODE 2.0)
        version: Version du modèle (ABACODE 2.0)
        status: Statut de validité (ABACODE 2.0)
    """
    from_basin: str
    to_basin: str
    probability: float
    distance_km: float
    current_speed: float
    
    # Métadonnées ABACODE 2.0
    source: str
    method: str
    uncertainty: float
    version: str
    status: str  # "measured" | "inferred" | "simulated"


class BiologicalConnectivityGraph:
    """
    Graphe de connectivité biologique
    
    Structure: Liste d'adjacence
    Type: Graphe orienté pondéré
    """
    
    def __init__(self):
        self.basins: Dict[str, Basin] = {}
        self.adjacency_list: Dict[str, List[LarvalFlow]] = {}
    
    def add_basin(self, basin: Basin):
        """
        Ajouter un bassin (nœud) - O(1)
        
        Args:
            basin: Bassin à ajouter
            
        Raises:
            ValueError: Si métadonnées ABACODE incomplètes
        """
        if not all([basin.source, basin.version, basin.status]):
            raise ValueError("Métadonnées ABACODE 2.0 incomplètes")
        
        if basin.status not in ["measured", "inferred", "simulated"]:
            raise ValueError(f"Statut invalide: {basin.status}")
        
        self.basins[basin.id] = basin
        if basin.id not in self.adjacency_list:
            self.adjacency_list[basin.id] = []
    
    def add_flow(self, flow: LarvalFlow):
        """
        Ajouter un flux larvaire (arête) - O(1)
        
        Args:
            flow: Flux larvaire à ajouter
            
        Raises:
            ValueError: Si métadonnées ABACODE incomplètes ou bassins inexistants
        """
        if not all([flow.source, flow.method, flow.version, flow.status]):
            raise ValueError("Métadonnées ABACODE 2.0 incomplètes")
        
        if flow.status not in ["measured", "inferred", "simulated"]:
            raise ValueError(f"Statut invalide: {flow.status}")
        
        if flow.from_basin not in self.basins:
            raise ValueError(f"Bassin source inexistant: {flow.from_basin}")
        
        if flow.to_basin not in self.basins:
            raise ValueError(f"Bassin destination inexistant: {flow.to_basin}")
        
        if flow.from_basin not in self.adjacency_list:
            self.adjacency_list[flow.from_basin] = []
        
        self.adjacency_list[flow.from_basin].append(flow)
    
    def dijkstra(self, start: str, end: str) -> Tuple[float, List[str]]:
        """
        Algorithme de Dijkstra pour trouver le chemin optimal
        
        Complexité: O((V + E) log V) avec heap
        
        Args:
            start: ID du bassin de départ
            end: ID du bassin d'arrivée
            
        Returns:
            (distance_totale, chemin)
            distance_totale = inf si aucun chemin trouvé
            chemin = [] si aucun chemin trouvé
        """
        if start not in self.basins or end not in self.basins:
            return (float('inf'), [])
        
        # Initialisation
        distances = {basin_id: float('inf') for basin_id in self.basins}
        distances[start] = 0.0
        previous = {basin_id: None for basin_id in self.basins}
        
        # Heap de priorité: (distance, basin_id)
        heap = [(0.0, start)]
        visited: Set[str] = set()
        
        while heap:
            current_dist, current_basin = heapq.heappop(heap)
            
            if current_basin in visited:
                continue
            
            visited.add(current_basin)
            
            # Si on a atteint la destination
            if current_basin == end:
                break
            
            # Explorer les voisins
            for flow in self.adjacency_list.get(current_basin, []):
                neighbor = flow.to_basin
                
                # Calcul de la "distance biologique"
                # Formule: distance_km / (probability * current_speed)
                # Plus la probabilité est élevée, plus le "coût" est faible
                biological_distance = flow.distance_km / (flow.probability * max(flow.current_speed, 0.1))
                
                new_dist = current_dist + biological_distance
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current_basin
                    heapq.heappush(heap, (new_dist, neighbor))
        
        # Reconstruction du chemin
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        # Si le chemin ne commence pas par start, aucun chemin trouvé
        if path[0] != start:
            return (float('inf'), [])
        
        return (distances[end], path)
    
    def get_reachable_basins(self, start: str, max_distance: float) -> List[Tuple[str, float]]:
        """
        Trouver tous les bassins atteignables depuis un bassin source
        dans une distance biologique maximale
        
        Args:
            start: ID du bassin de départ
            max_distance: Distance biologique maximale
            
        Returns:
            [(basin_id, distance), ...] trié par distance croissante
        """
        reachable = []
        
        for basin_id in self.basins:
            if basin_id == start:
                continue
            
            distance, path = self.dijkstra(start, basin_id)
            
            if distance <= max_distance:
                reachable.append((basin_id, distance))
        
        # Trier par distance croissante
        reachable.sort(key=lambda x: x[1])
        
        return reachable
    
    def analyze_connectivity(self) -> dict:
        """
        Analyse de la connectivité globale du réseau
        
        Returns:
            Dictionnaire avec statistiques du graphe
        """
        total_flows = sum(len(flows) for flows in self.adjacency_list.values())
        avg_degree = total_flows / len(self.basins) if self.basins else 0
        
        # Identifier les bassins "hubs" (forte connectivité)
        hubs = []
        for basin_id, flows in self.adjacency_list.items():
            if len(flows) > avg_degree * 1.5:
                hubs.append((basin_id, len(flows)))
        
        # Identifier les bassins isolés (aucune connexion sortante)
        isolated = [basin_id for basin_id in self.basins if len(self.adjacency_list.get(basin_id, [])) == 0]
        
        return {
            "total_basins": len(self.basins),
            "total_flows": total_flows,
            "average_degree": avg_degree,
            "hubs": hubs,
            "isolated_basins": isolated
        }
    
    def get_basin_info(self, basin_id: str) -> Optional[dict]:
        """
        Informations détaillées sur un bassin
        
        Args:
            basin_id: ID du bassin
            
        Returns:
            Dictionnaire avec informations du bassin, ou None si inexistant
        """
        if basin_id not in self.basins:
            return None
        
        basin = self.basins[basin_id]
        outgoing_flows = self.adjacency_list.get(basin_id, [])
        
        # Compter les flux entrants
        incoming_flows = []
        for other_basin_id, flows in self.adjacency_list.items():
            for flow in flows:
                if flow.to_basin == basin_id:
                    incoming_flows.append(flow)
        
        return {
            "id": basin.id,
            "name": basin.name,
            "coordinates": basin.coordinates,
            "capacity": basin.capacity,
            "outgoing_flows": len(outgoing_flows),
            "incoming_flows": len(incoming_flows),
            "total_connectivity": len(outgoing_flows) + len(incoming_flows),
            "source": basin.source,
            "version": basin.version,
            "status": basin.status
        }
    
    def clear(self):
        """Vider le graphe"""
        self.basins.clear()
        self.adjacency_list.clear()


if __name__ == "__main__":
    # Test rapide
    print("=== Test BiologicalConnectivityGraph ===")
    
    graph = BiologicalConnectivityGraph()
    
    # Ajouter des bassins
    barag = Basin(
        id="BARAG",
        name="Bassin d'Arcachon - Grand Banc",
        coordinates=(44.6667, -1.1667),
        capacity=150,
        source="IFREMER_CARTOGRAPHY",
        version="v3.0.1",
        status="measured"
    )
    
    eyrac = Basin(
        id="EYRAC",
        name="Eyrac",
        coordinates=(44.7000, -1.2000),
        capacity=80,
        source="IFREMER_CARTOGRAPHY",
        version="v3.0.1",
        status="measured"
    )
    
    graph.add_basin(barag)
    graph.add_basin(eyrac)
    
    # Ajouter un flux larvaire
    flow = LarvalFlow(
        from_basin="BARAG",
        to_basin="EYRAC",
        probability=0.65,
        distance_km=5.2,
        current_speed=0.15,
        source="IFREMER_MODEL",
        method="hydrodynamic_simulation",
        uncertainty=0.12,
        version="v3.0.1",
        status="simulated"
    )
    
    graph.add_flow(flow)
    
    print(f"Bassins: {len(graph.basins)}")
    print(f"Flux larvaires: {sum(len(f) for f in graph.adjacency_list.values())}")
    
    # Calculer le chemin optimal
    distance, path = graph.dijkstra("BARAG", "EYRAC")
    print(f"\nChemin BARAG → EYRAC:")
    print(f"  Distance biologique: {distance:.2f}")
    print(f"  Chemin: {' → '.join(path)}")
    
    # Analyse de connectivité
    stats = graph.analyze_connectivity()
    print(f"\nStatistiques:")
    print(f"  Degré moyen: {stats['average_degree']:.2f}")
    
    print("\n✓ Test réussi")
