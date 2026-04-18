"""
Tests Unitaires - Structures de Données
Conformité ABACODE 2.0

Exécution: python tests/test_data_structures.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from src.data_structures import (
    AlertHeap, Alert, AlertPriority,
    VesselHashTable, Vessel,
    BiologicalConnectivityGraph, Basin, LarvalFlow
)


def test_alert_heap():
    """Test du Heap d'alertes"""
    print("\n=== TEST ALERT HEAP ===")
    
    heap = AlertHeap()
    
    # Test 1: Insertion et peek
    alert1 = Alert(
        timestamp=datetime.now(),
        station_id="BARAG",
        parameter="pH",
        value=7.55,
        threshold=7.6,
        priority=AlertPriority.CRITICAL,
        message="pH critique",
        source="IFREMER",
        method="sensor",
        uncertainty=0.02,
        version="v3.0.1",
        status="measured"
    )
    
    heap.insert(alert1)
    assert heap.size == 1, "Taille incorrecte après insertion"
    assert heap.peek().priority == AlertPriority.CRITICAL, "Peek incorrect"
    print("✓ Test 1: Insertion et peek")
    
    # Test 2: Priorité
    alert2 = Alert(
        timestamp=datetime.now(),
        station_id="EYRAC",
        parameter="O2",
        value=150.0,
        threshold=140.0,
        priority=AlertPriority.MEDIUM,
        message="O2 faible",
        source="VPS",
        method="calculated",
        uncertainty=5.0,
        version="v3.0.1",
        status="inferred"
    )
    
    heap.insert(alert2)
    assert heap.peek().priority == AlertPriority.CRITICAL, "Priorité incorrecte"
    print("✓ Test 2: Gestion des priorités")
    
    # Test 3: Extraction
    extracted = heap.extract_min()
    assert extracted.priority == AlertPriority.CRITICAL, "Extraction incorrecte"
    assert heap.size == 1, "Taille incorrecte après extraction"
    print("✓ Test 3: Extraction")
    
    # Test 4: Validation ABACODE
    try:
        invalid_alert = Alert(
            timestamp=datetime.now(),
            station_id="TEST",
            parameter="pH",
            value=7.5,
            threshold=7.6,
            priority=AlertPriority.LOW,
            message="Test",
            source="",  # Manquant
            method="test",
            uncertainty=0.0,
            version="v3.0.1",
            status="measured"
        )
        heap.insert(invalid_alert)
        assert False, "Devrait rejeter métadonnées incomplètes"
    except ValueError:
        print("✓ Test 4: Validation ABACODE")
    
    # Test 5: Statistiques
    heap.clear()
    for i in range(10):
        priority = AlertPriority.CRITICAL if i < 3 else AlertPriority.MEDIUM
        alert = Alert(
            timestamp=datetime.now(),
            station_id=f"STATION_{i}",
            parameter="pH",
            value=7.5,
            threshold=7.6,
            priority=priority,
            message=f"Alert {i}",
            source="TEST",
            method="test",
            uncertainty=0.02,
            version="v3.0.1",
            status="simulated"
        )
        heap.insert(alert)
    
    stats = heap.get_statistics()
    assert stats['size'] == 10, "Statistiques incorrectes"
    assert stats['critical'] == 3, "Comptage CRITICAL incorrect"
    print("✓ Test 5: Statistiques")
    
    print("✅ ALERT HEAP: Tous les tests réussis")
    return True


def test_vessel_hashtable():
    """Test de la Table de Hachage AIS"""
    print("\n=== TEST VESSEL HASHTABLE ===")
    
    ais = VesselHashTable()
    
    # Test 1: Insertion et recherche
    vessel1 = Vessel(
        mmsi=228123456,
        name="CHALUTIER 1",
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
    
    ais.insert(vessel1)
    found = ais.search(228123456)
    assert found is not None, "Navire non trouvé"
    assert found.name == "CHALUTIER 1", "Nom incorrect"
    print("✓ Test 1: Insertion et recherche")
    
    # Test 2: Mise à jour
    vessel1_updated = Vessel(
        mmsi=228123456,
        name="CHALUTIER 1 UPDATED",
        vessel_type="fishing",
        length=25.0,
        beam=6.5,
        draft=2.3,
        last_position=(44.7000, -1.2000),
        last_update=datetime.now(),
        source="AIS_LIVE",
        uncertainty_position=10.0,
        version="v3.0.1",
        status="measured"
    )
    
    ais.insert(vessel1_updated)
    found = ais.search(228123456)
    assert found.name == "CHALUTIER 1 UPDATED", "Mise à jour échouée"
    assert ais.size == 1, "Taille incorrecte après mise à jour"
    print("✓ Test 2: Mise à jour")
    
    # Test 3: Suppression
    deleted = ais.delete(228123456)
    assert deleted == True, "Suppression échouée"
    assert ais.search(228123456) is None, "Navire encore présent"
    assert ais.size == 0, "Taille incorrecte après suppression"
    print("✓ Test 3: Suppression")
    
    # Test 4: Performance (collisions)
    ais.clear()
    for i in range(100):
        vessel = Vessel(
            mmsi=200000000 + i,
            name=f"VESSEL_{i}",
            vessel_type="cargo",
            length=100.0,
            beam=20.0,
            draft=8.0,
            last_position=(44.0 + i*0.01, -1.0 + i*0.01),
            last_update=datetime.now(),
            source="AIS_LIVE",
            uncertainty_position=10.0,
            version="v3.0.1",
            status="measured"
        )
        ais.insert(vessel)
    
    stats = ais.get_statistics()
    assert stats['size'] == 100, "Taille incorrecte"
    assert stats['load_factor'] < 0.02, "Facteur de charge trop élevé"
    print(f"✓ Test 4: Performance (collision rate: {stats['collision_rate']:.2f}%)")
    
    # Test 5: Validation ABACODE
    try:
        invalid_vessel = Vessel(
            mmsi=999999999,
            name="INVALID",
            vessel_type="test",
            length=10.0,
            beam=5.0,
            draft=2.0,
            last_position=(0.0, 0.0),
            last_update=datetime.now(),
            source="",  # Manquant
            uncertainty_position=0.0,
            version="v3.0.1",
            status="measured"
        )
        ais.insert(invalid_vessel)
        assert False, "Devrait rejeter métadonnées incomplètes"
    except ValueError:
        print("✓ Test 5: Validation ABACODE")
    
    print("✅ VESSEL HASHTABLE: Tous les tests réussis")
    return True


def test_connectivity_graph():
    """Test du Graphe de Connectivité"""
    print("\n=== TEST CONNECTIVITY GRAPH ===")
    
    graph = BiologicalConnectivityGraph()
    
    # Test 1: Ajout de bassins
    basin1 = Basin(
        id="BARAG",
        name="Grand Banc",
        coordinates=(44.6667, -1.1667),
        capacity=150,
        source="IFREMER",
        version="v3.0.1",
        status="measured"
    )
    
    basin2 = Basin(
        id="EYRAC",
        name="Eyrac",
        coordinates=(44.7000, -1.2000),
        capacity=80,
        source="IFREMER",
        version="v3.0.1",
        status="measured"
    )
    
    graph.add_basin(basin1)
    graph.add_basin(basin2)
    assert len(graph.basins) == 2, "Nombre de bassins incorrect"
    print("✓ Test 1: Ajout de bassins")
    
    # Test 2: Ajout de flux
    flow = LarvalFlow(
        from_basin="BARAG",
        to_basin="EYRAC",
        probability=0.65,
        distance_km=5.2,
        current_speed=0.15,
        source="IFREMER_MODEL",
        method="simulation",
        uncertainty=0.12,
        version="v3.0.1",
        status="simulated"
    )
    
    graph.add_flow(flow)
    assert len(graph.adjacency_list["BARAG"]) == 1, "Flux non ajouté"
    print("✓ Test 2: Ajout de flux")
    
    # Test 3: Dijkstra
    distance, path = graph.dijkstra("BARAG", "EYRAC")
    assert path == ["BARAG", "EYRAC"], "Chemin incorrect"
    assert distance > 0, "Distance incorrecte"
    print(f"✓ Test 3: Dijkstra (distance: {distance:.2f})")
    
    # Test 4: Bassins atteignables
    basin3 = Basin(
        id="COMPRIAN",
        name="Comprian",
        coordinates=(44.7500, -1.2500),
        capacity=60,
        source="IFREMER",
        version="v3.0.1",
        status="measured"
    )
    graph.add_basin(basin3)
    
    flow2 = LarvalFlow(
        from_basin="EYRAC",
        to_basin="COMPRIAN",
        probability=0.50,
        distance_km=3.8,
        current_speed=0.12,
        source="IFREMER_MODEL",
        method="simulation",
        uncertainty=0.15,
        version="v3.0.1",
        status="simulated"
    )
    graph.add_flow(flow2)
    
    reachable = graph.get_reachable_basins("BARAG", max_distance=1000.0)
    assert len(reachable) == 2, "Bassins atteignables incorrect"
    print("✓ Test 4: Bassins atteignables")
    
    # Test 5: Analyse de connectivité
    stats = graph.analyze_connectivity()
    assert stats['total_basins'] == 3, "Nombre de bassins incorrect"
    assert stats['total_flows'] == 2, "Nombre de flux incorrect"
    print("✓ Test 5: Analyse de connectivité")
    
    # Test 6: Validation ABACODE
    try:
        invalid_basin = Basin(
            id="INVALID",
            name="Invalid",
            coordinates=(0.0, 0.0),
            capacity=0,
            source="",  # Manquant
            version="v3.0.1",
            status="measured"
        )
        graph.add_basin(invalid_basin)
        assert False, "Devrait rejeter métadonnées incomplètes"
    except ValueError:
        print("✓ Test 6: Validation ABACODE")
    
    print("✅ CONNECTIVITY GRAPH: Tous les tests réussis")
    return True


def run_all_tests():
    """Exécuter tous les tests"""
    print("=" * 60)
    print("TESTS UNITAIRES - STRUCTURES DE DONNÉES")
    print("Conformité ABACODE 2.0")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("AlertHeap", test_alert_heap()))
    except Exception as e:
        print(f"❌ ALERT HEAP: {e}")
        results.append(("AlertHeap", False))
    
    try:
        results.append(("VesselHashTable", test_vessel_hashtable()))
    except Exception as e:
        print(f"❌ VESSEL HASHTABLE: {e}")
        results.append(("VesselHashTable", False))
    
    try:
        results.append(("ConnectivityGraph", test_connectivity_graph()))
    except Exception as e:
        print(f"❌ CONNECTIVITY GRAPH: {e}")
        results.append(("ConnectivityGraph", False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("✓ Conformité ABACODE 2.0 validée")
        print("✓ Prêt pour déploiement en production")
        return True
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les erreurs ci-dessus")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
