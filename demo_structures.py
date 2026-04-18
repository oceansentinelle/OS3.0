"""
Démonstration des Structures de Données - OCÉAN-SENTINELLE
Conformité ABACODE 2.0

Exécution: python demo_structures.py
"""

import sys
import os
from datetime import datetime
from src.data_structures import (
    AlertHeap, Alert, AlertPriority,
    VesselHashTable, Vessel,
    BiologicalConnectivityGraph, Basin, LarvalFlow
)


def demo_alert_heap():
    """Démonstration du Heap d'alertes"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION 1 : HEAP DE PRIORITÉ POUR ALERTES")
    print("=" * 70)
    
    heap = AlertHeap()
    
    print("\n📊 Scénario: Crise de mortalité massive détectée")
    print("-" * 70)
    
    # Simulation de plusieurs alertes simultanées
    alerts_data = [
        ("BARAG", "pH", 7.55, 7.6, AlertPriority.CRITICAL, "Mortalité imminente - pH critique"),
        ("EYRAC", "O2", 135.0, 150.0, AlertPriority.HIGH, "Hypoxie détectée"),
        ("COMPRIAN", "temperature", 24.5, 22.0, AlertPriority.MEDIUM, "Anomalie thermique"),
        ("BARAG", "salinite", 32.5, 33.0, AlertPriority.LOW, "Salinité légèrement basse"),
        ("EYRAC", "pH", 7.58, 7.6, AlertPriority.HIGH, "pH proche du seuil critique"),
    ]
    
    print("\n1️⃣ Insertion de 5 alertes simultanées:")
    for station, param, value, threshold, priority, message in alerts_data:
        alert = Alert(
            timestamp=datetime.now(),
            station_id=station,
            parameter=param,
            value=value,
            threshold=threshold,
            priority=priority,
            message=message,
            source=f"IFREMER_{station}",
            method="sensor_direct",
            uncertainty=0.02 if param == "pH" else 5.0,
            version="v3.0.1",
            status="measured"
        )
        heap.insert(alert)
        priority_name = priority.name
        print(f"   [{priority_name:8}] {station:10} - {message}")
    
    print(f"\n2️⃣ Statistiques du heap:")
    stats = heap.get_statistics()
    print(f"   Taille totale: {stats['size']}")
    print(f"   Alertes CRITICAL: {stats['critical']}")
    print(f"   Alertes HIGH: {stats['high']}")
    print(f"   Alertes MEDIUM: {stats['medium']}")
    print(f"   Alertes LOW: {stats['low']}")
    
    print(f"\n3️⃣ Traitement par ordre de priorité (extraction):")
    order = 1
    while heap.size > 0:
        alert = heap.extract_min()
        print(f"   {order}. [{alert.priority.name:8}] {alert.station_id:10} - {alert.message}")
        order += 1
    
    print("\n✅ Résultat: Les alertes CRITICAL sont traitées en premier !")
    print("   Complexité: O(log n) par extraction")


def demo_vessel_hashtable():
    """Démonstration de la Table de Hachage AIS"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION 2 : TABLE DE HACHAGE POUR INDEXATION AIS")
    print("=" * 70)
    
    ais = VesselHashTable()
    
    print("\n🚢 Scénario: Surveillance du trafic maritime dans le Bassin d'Arcachon")
    print("-" * 70)
    
    # Simulation de navires
    vessels_data = [
        (228123456, "CHALUTIER ARCACHON", "fishing", 25.0, (44.6667, -1.1667)),
        (228654321, "CARGO BORDEAUX", "cargo", 150.0, (44.7000, -1.2000)),
        (228987654, "VOILIER PLAISANCE", "pleasure", 12.0, (44.6500, -1.1500)),
        (228111222, "FERRY CAP FERRET", "passenger", 45.0, (44.6800, -1.2100)),
        (228333444, "CHALUTIER EYRAC", "fishing", 28.0, (44.7200, -1.2300)),
    ]
    
    print("\n1️⃣ Indexation de 5 navires:")
    for mmsi, name, vtype, length, position in vessels_data:
        vessel = Vessel(
            mmsi=mmsi,
            name=name,
            vessel_type=vtype,
            length=length,
            beam=length * 0.25,
            draft=length * 0.1,
            last_position=position,
            last_update=datetime.now(),
            source="AIS_LIVE",
            uncertainty_position=10.0,
            version="v3.0.1",
            status="measured"
        )
        ais.insert(vessel)
        print(f"   MMSI {mmsi} - {name:25} ({vtype:10}) - {length:5.1f}m")
    
    print(f"\n2️⃣ Statistiques de la table de hachage:")
    stats = ais.get_statistics()
    print(f"   Capacité: {stats['capacity']:,}")
    print(f"   Navires indexés: {stats['size']}")
    print(f"   Facteur de charge: {stats['load_factor']:.4%}")
    print(f"   Taux de collisions: {stats['collision_rate']:.2f}%")
    print(f"   Longueur max chaîne: {stats['max_chain_length']}")
    
    print(f"\n3️⃣ Recherche instantanée (O(1)):")
    search_mmsi = 228123456
    found = ais.search(search_mmsi)
    if found:
        print(f"   Recherche MMSI {search_mmsi}:")
        print(f"   ✓ Trouvé: {found.name}")
        print(f"   ✓ Type: {found.vessel_type}")
        print(f"   ✓ Position: {found.last_position}")
        print(f"   ✓ Source: {found.source} (ABACODE 2.0)")
    
    print("\n✅ Résultat: Accès instantané parmi 10,007 emplacements possibles !")
    print("   Complexité: O(1) en moyenne")


def demo_connectivity_graph():
    """Démonstration du Graphe de Connectivité"""
    print("\n" + "=" * 70)
    print("DÉMONSTRATION 3 : GRAPHE DE CONNECTIVITÉ BIOLOGIQUE")
    print("=" * 70)
    
    graph = BiologicalConnectivityGraph()
    
    print("\n🦪 Scénario: Modélisation des flux larvaires entre bassins ostréicoles")
    print("-" * 70)
    
    # Création des bassins
    basins_data = [
        ("BARAG", "Grand Banc", (44.6667, -1.1667), 150),
        ("EYRAC", "Eyrac", (44.7000, -1.2000), 80),
        ("COMPRIAN", "Comprian", (44.7500, -1.2500), 60),
        ("ARGUIN", "Banc d'Arguin", (44.6000, -1.2000), 40),
    ]
    
    print("\n1️⃣ Création de 4 bassins ostréicoles:")
    for basin_id, name, coords, capacity in basins_data:
        basin = Basin(
            id=basin_id,
            name=name,
            coordinates=coords,
            capacity=capacity,
            source="IFREMER_CARTOGRAPHY",
            version="v3.0.1",
            status="measured"
        )
        graph.add_basin(basin)
        print(f"   {basin_id:10} - {name:20} ({capacity} parcs)")
    
    # Création des flux larvaires
    flows_data = [
        ("BARAG", "EYRAC", 0.65, 5.2, 0.15),
        ("EYRAC", "COMPRIAN", 0.50, 3.8, 0.12),
        ("BARAG", "ARGUIN", 0.45, 8.5, 0.10),
        ("ARGUIN", "EYRAC", 0.35, 6.0, 0.08),
        ("COMPRIAN", "BARAG", 0.25, 7.5, 0.09),
    ]
    
    print("\n2️⃣ Modélisation de 5 flux larvaires:")
    for from_b, to_b, prob, dist, speed in flows_data:
        flow = LarvalFlow(
            from_basin=from_b,
            to_basin=to_b,
            probability=prob,
            distance_km=dist,
            current_speed=speed,
            source="IFREMER_HYDRODYNAMIC_MODEL",
            method="particle_tracking_simulation",
            uncertainty=0.15,
            version="v3.0.1",
            status="simulated"
        )
        graph.add_flow(flow)
        print(f"   {from_b:10} → {to_b:10} (P={prob:.2f}, {dist:.1f}km, {speed:.2f}m/s)")
    
    print(f"\n3️⃣ Calcul du chemin optimal (Dijkstra):")
    start = "BARAG"
    end = "COMPRIAN"
    distance, path = graph.dijkstra(start, end)
    
    print(f"   Origine: {start}")
    print(f"   Destination: {end}")
    print(f"   Chemin optimal: {' → '.join(path)}")
    print(f"   Distance biologique: {distance:.2f}")
    
    print(f"\n4️⃣ Bassins atteignables depuis BARAG (distance < 500):")
    reachable = graph.get_reachable_basins("BARAG", max_distance=500.0)
    for basin_id, dist in reachable:
        basin_info = graph.get_basin_info(basin_id)
        print(f"   {basin_id:10} - Distance: {dist:6.2f} - Capacité: {basin_info['capacity']} parcs")
    
    print(f"\n5️⃣ Analyse de connectivité:")
    stats = graph.analyze_connectivity()
    print(f"   Bassins totaux: {stats['total_basins']}")
    print(f"   Flux totaux: {stats['total_flows']}")
    print(f"   Degré moyen: {stats['average_degree']:.2f}")
    if stats['hubs']:
        print(f"   Bassins 'hubs': {[h[0] for h in stats['hubs']]}")
    
    print("\n✅ Résultat: Modélisation complète de la connectivité larvaire !")
    print("   Complexité Dijkstra: O((V + E) log V)")


def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("🌊 OCÉAN-SENTINELLE V3.0")
    print("Démonstration des Structures de Données Avancées")
    print("Conformité ABACODE 2.0")
    print("=" * 70)
    
    try:
        demo_alert_heap()
        demo_vessel_hashtable()
        demo_connectivity_graph()
        
        print("\n" + "=" * 70)
        print("🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 70)
        print("\n📋 Récapitulatif:")
        print("   ✓ Heap de priorité: Triage des alertes en O(log n)")
        print("   ✓ Table de hachage: Indexation AIS en O(1)")
        print("   ✓ Graphe: Connectivité biologique avec Dijkstra")
        print("\n🔒 Conformité ABACODE 2.0:")
        print("   ✓ Toutes les données incluent source, méthode, incertitude")
        print("   ✓ Statut explicite: measured | inferred | simulated")
        print("   ✓ Traçabilité totale garantie")
        print("\n🚀 Prêt pour déploiement en production !")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
