# Rapport d'Architecture des Systèmes de Données pour la Plateforme GeM OCÉAN-SENTINELLE

**Optimisation Algorithmique et Gouvernance ABACODE 2.0**

---

## L'Essentiel

L'optimisation de la plateforme OCÉAN-SENTINELLE repose sur l'intégration stratégique de huit structures de données fondamentales pour transformer les flux de capteurs marins en indicateurs décisionnels résilients face aux crises ostréicoles. Ce rapport détaille l'application des tableaux, listes, piles, files, tables de hachage, arbres et graphes selon la méthodologie ABACODE 2.0, garantissant une traçabilité totale et une performance algorithmique adaptée aux contraintes du Golfe de Gascogne. L'architecture hybride proposée sécurise la gestion des alertes de mortalité et la prédiction de trajectoires AIS tout en respectant une hiérarchie stricte où la stabilité et la sécurité prévalent sur la complexité de l'intelligence artificielle.

---

## Analyse Profonde

### Fondements de la Mission OCÉAN-SENTINELLE et Cadre de Gouvernance

La mission OCÉAN-SENTINELLE s'établit comme une infrastructure critique d'aide à la décision pour la filière conchylicole de Nouvelle-Aquitaine, ciblant spécifiquement les défis posés par l'acidification océanique, les changements climatiques et les épisodes de mortalité massive des huîtres. La plateforme fonctionne sous le régime strict de la méthode **ABACODE 2.0**, laquelle impose que chaque donnée traitée soit accompagnée de métadonnées précises :

- **Source** : Origine de la donnée (capteur, modèle, base externe)
- **Date** : Horodatage précis d'acquisition
- **Méthode de calcul** : Algorithme ou formule utilisée
- **Incertitude associée** : Marge d'erreur quantifiée
- **Version du modèle** : Traçabilité des évolutions logicielles
- **Statut de validité** : Mesuré, inféré ou simulé

L'architecture logicielle de type **MVP (Minimum Viable Product)** est hébergée sur un serveur privé virtuel (VPS) dont les ressources (2 vCPU, 8 GB RAM) exigent une efficacité algorithmique optimale. Le choix des structures de données n'est donc pas une simple préférence technique, mais une **nécessité opérationnelle** pour garantir la stabilité du système, priorité absolue avant même la performance ou l'innovation en IA.

L'usage de technologies comme **pgvector** au sein de PostgreSQL souligne l'importance d'une indexation vectorielle avancée pour les systèmes de génération augmentée par récupération (RAG), essentiels pour traiter la documentation scientifique volumineuse sur l'acidification.

---

## Chapitre 1 : Les Structures de Données Linéaires et l'Ingestion de Flux Capteurs

La première étape de la chaîne de valeur d'OCÉAN-SENTINELLE concerne l'acquisition de données environnementales brutes (pH, température, salinité, oxygène dissous). Pour ces flux, deux structures fondamentales s'opposent et se complètent : le **tableau** et la **liste chaînée**.

### 1.1 Le Tableau (Array) et l'Analogie du Parking Numéroté

Le tableau est une structure où les éléments sont stockés dans des blocs de mémoire contigus, permettant un accès instantané par index avec une complexité de **O(1)**. L'analogie du parking numéroté est ici particulièrement illustrative : si chaque place de parking est un index mémoire, accéder à la voiture garée à la place 42 ne nécessite pas de vérifier les places 1 à 41.

Dans le contexte d'ingénierie logicielle pour OCÉAN-SENTINELLE, les tableaux sont privilégiés pour le stockage des **séries temporelles à fréquence fixe**. Par exemple, les relevés de pHT (pH total) effectués toutes les minutes sur une période de 24 heures sont stockés dans un tableau de 1440 entrées. La localité spatiale des tableaux favorise l'utilisation du cache CPU, rendant les itérations pour le calcul de moyennes mobiles extrêmement rapides.

Cependant, l'insertion d'une donnée manquante au milieu d'un tableau est coûteuse **O(n)** car elle nécessite de décaler physiquement les éléments suivants en mémoire.

| Opération | Complexité | Justification Technique |
|-----------|-----------|------------------------|
| Accès | O(1) | Calcul d'adresse direct : `base_address + (index × element_size)` |
| Insertion | O(n) | Nécessite le déplacement des données contigües |
| Suppression | O(n) | Nécessite le comblement de l'espace vide |
| Recherche | O(n) | Parcours linéaire obligatoire si non trié |

### 1.2 La Liste Chaînée (Linked List) et l'Analogie de la Chasse au Trésor

À l'opposé du tableau, la liste chaînée ne requiert pas de mémoire contiguë. Chaque élément (nœud) stocke sa propre valeur et l'adresse mémoire du nœud suivant. L'analogie est celle d'une chasse au trésor : chaque indice trouvé contient l'emplacement du prochain indice, obligeant à parcourir la chaîne depuis le début pour atteindre un élément spécifique.

Pour OCÉAN-SENTINELLE, les listes chaînées sont idéales pour la gestion des **flux asynchrones**, comme les signalements de mortalité envoyés par les ostréiculteurs via mobile. Puisque le nombre de signalements est imprévisible, la liste peut croître dynamiquement sans nécessiter de réallocation massive de mémoire.

L'insertion ou la suppression d'un nœud est instantanée **O(1)** si l'on possède déjà le pointeur sur l'élément précédent, car il suffit de modifier deux références mémoires.

---

## Chapitre 2 : Structures Opérationnelles et Gestion des Flux de Travail

La gestion des processus internes de la plateforme, tels que l'annulation d'actions ou le traitement séquentiel des messages capteurs, repose sur les **piles** et les **files d'attente**.

### 2.1 La Pile (Stack) et l'Analogie de la Pile d'Assiettes

La pile suit le principe **LIFO (Last-In, First-Out)**. Seule la donnée au sommet est accessible. C'est l'analogie de la pile d'assiettes : la dernière assiette posée sur le haut est nécessairement la première que l'on doit retirer pour ne pas briser l'ensemble.

En ingénierie logicielle, la pile est la colonne vertébrale des fonctions de navigation et de simulation. Pour OCÉAN-SENTINELLE, elle est utilisée dans :

- **Le mécanisme d'annulation (Ctrl+Z)** : Chaque modification d'un paramètre de simulation (ex: augmentation du CO2 atmosphérique) est empilée. Pour revenir en arrière, on dépile le dernier état.
- **La gestion de la récursion** : Pour le calcul des équilibres chimiques complexes du carbonate, où les fonctions s'appellent elles-mêmes en empilant les contextes d'exécution.

### 2.2 La File d'Attente (Queue) et l'Analogie de la File à la Banque

La file d'attente respecte le principe **FIFO (First-In, First-Out)**. Le premier élément entré est le premier traité. L'analogie est celle d'une file d'attente à la banque : le client arrivé en premier est servi en premier.

OCÉAN-SENTINELLE utilise des files d'attente pour la gestion de sa **Worker API**. Les données massives provenant des réseaux IoT (via MQTT) sont placées dans une file d'attente (comme RabbitMQ ou Kafka) pour être traitées par ordre d'arrivée par les exécutants de "skills" (compétences). Cela évite la surcharge du serveur lors des pics de transmission de données.

| Structure | Principe | Cas d'Utilisation Sentinel | Analogie |
|-----------|----------|---------------------------|----------|
| Pile | LIFO | Historique de navigation, Undo/Redo | Pile d'assiettes |
| File | FIFO | Traitement asynchrone des alertes capteurs | File d'attente |

---

## Chapitre 3 : Indexation et Recherche Rapide dans les Données Maritimes

L'un des enjeux majeurs est l'identification instantanée d'un navire parmi des milliers (via son MMSI) ou la recherche d'une constante chimique dans une base de données historique.

### 3.1 La Table de Hachage (Hash Table) et l'Analogie du Dictionnaire

La table de hachage est souvent décrite comme la structure la plus importante en génie logiciel. Elle permet un accès quasi instantané **O(1)** en moyenne à une valeur associée à une clé unique. L'analogie est celle du dictionnaire papier : pour trouver la définition du mot "Ostréiculture", on n'examine pas chaque page, on utilise l'index alphabétique pour sauter directement à la section "O".

Dans le système OCÉAN-SENTINELLE, les tables de hachage sont utilisées pour :

- **L'indexation des données AIS** : Le numéro MMSI du navire sert de clé. La fonction de hachage calcule instantanément l'adresse mémoire où sont stockées les caractéristiques du navire (longueur, tirant d'eau, cargaison).
- **Le cache applicatif** : Stocker les résultats de calculs thermodynamiques coûteux (comme l'état de saturation de l'aragonite ΩArag) pour éviter de les recalculer si les entrées (T°, S, Alk) sont identiques.

### 3.2 L'Arbre Binaire de Recherche (BST) et l'Analogie de "Devine le Nombre"

Un arbre binaire de recherche organise les données de manière hiérarchique. Pour chaque nœud, les valeurs plus petites sont à gauche et les plus grandes à droite. L'analogie est le jeu de "Devine le nombre" entre 1 et 100 : si l'on propose 50 et que la réponse est "plus grand", on a éliminé la moitié des possibilités d'un seul coup.

Pour OCÉAN-SENTINELLE, les arbres (sous forme de B-Trees ou de partitions géospatiales) permettent d'effectuer des **requêtes de plage (range queries)**. Par exemple : "Extraire tous les relevés de température entre 15°C et 18°C". Une table de hachage ne peut pas faire cela efficacement, tandis qu'un arbre binaire permet de trouver ces valeurs en **O(log n)**.

---

## Chapitre 4 : Gestion des Priorités et Analyse de Réseaux

Certaines situations exigent de traiter les informations non pas par ordre d'arrivée, mais par ordre d'importance, ou d'analyser les relations entre entités géographiques.

### 4.1 L'Arbre de Priorité (Heap) et l'Analogie du Service d'Urgences

Le Heap est une structure d'arbre où l'élément ayant la plus haute priorité est toujours à la racine. L'analogie est le triage aux urgences d'un hôpital : une personne arrivant avec une détresse respiratoire sera traitée avant une personne arrivée plus tôt pour une entorse, car sa "valeur de priorité" est supérieure.

**Application dans OCÉAN-SENTINELLE :**

- **Système d'Alertes Critiques** : Si le système reçoit simultanément 1000 signaux, le Heap placera en tête de file l'alerte de "mortalité imminente" détectée par des capteurs de pHT et d'oxygène, avant les notifications de maintenance logicielle.
- **Algorithme de Dijkstra** : Pour calculer la route la plus rapide d'un navire de surveillance, le Heap permet d'extraire à chaque étape le nœud du graphe ayant la distance cumulée minimale.

### 4.2 Le Graphe (Graph) et l'Analogie des Réseaux Sociaux ou Google Maps

Le graphe est la structure la plus complexe, composée de nœuds (sommets) reliés par des liens (arêtes). Il n'y a pas de hiérarchie fixe ; chaque nœud peut être connecté à n'importe quel autre. L'analogie est celle d'un réseau social (qui est ami avec qui) ou de Google Maps (quelles villes sont reliées par quelles routes).

Pour OCÉAN-SENTINELLE, les graphes sont utilisés pour :

- **Modélisation du trafic maritime** : Les ports et les zones de mouillage sont des nœuds, et les trajectoires AIS sont des arêtes. Cela permet de détecter des anomalies (navires s'écartant des routes habituelles près des parcs à huîtres).
- **Analyse de connectivité biologique** : Modéliser comment les larves d'huîtres se déplacent entre différents bassins en fonction des courants marins, chaque bassin étant un nœud du graphe.

| Structure | Analogie | Opération Critique | Application Maritime |
|-----------|----------|-------------------|---------------------|
| Heap | Service Urgences | Extract-Max O(log n) | Alerte de mortalité massive |
| Graphe | Google Maps | BFS / Dijkstra | Optimisation de trajectoire AIS |

---

## Chapitre 5 : Intégration ABACODE 2.0 et Couche de Consultation Assistée (ACL)

L'utilisation de ces structures de données doit se conformer aux exigences de preuve et de traçabilité définies dans le bloc d'instructions ACL v1.0. Chaque insertion dans une structure de données (ex: ajouter une valeur de pH dans un Tableau) doit être enregistrée avec son statut de vérité.

### Cycle C3 — Application Pratique sur les Seuils de pH

Conformément à la procédure C3, une consultation a été effectuée pour stabiliser les variables de simulation :

**C1 — CADRER**
- **Question** : Quels sont les seuils critiques de pH provoquant une mortalité des larves de *Crassostrea gigas* dans le Bassin d'Arcachon?
- **Succès** : Identification d'une valeur de pHT inférieure à 7.6.

**C2 — COLLECTER**
- Source 1 : Ifremer (2025). Rapports de surveillance locale (Mesuré).
- Source 2 : Findlay et al. (2022). Synthèse globale sur l'acidification (Simulé).
- Source 3 : Données instrumentées Ocean Sentinel (2026). Capteurs pHT (Mesuré).

**C3 — CONTRÔLER**
- **Fiabilité** : Les données Ifremer sont prioritaires (Local-first).
- **Confirmation** : Un pH inférieur à 7.7 induit un stress métabolique significatif.
- **Incertitude** : La variabilité nycthémérale du pH en zone côtière reste complexe à simuler sans alcalinité totale mesurée.

### Analyse de Fiabilité des Algorithmes

L'ingénierie logicielle d'OCÉAN-SENTINELLE refuse l'invention de chiffres. Si une variable manque (ex: alcalinité manquante pour calculer ΩArag), le système doit utiliser une structure de type **"Option"** ou **"Null"** gérée explicitement pour éviter toute dérive de simulation. En cas de conflit de sources entre une tendance globale et une mesure Ifremer, la stratégie ABACODE impose de trancher par la donnée locale instrumentée.

---

## Chapitre 6 : Simulation et Scénarios 2050

Pour produire des scénarios à l'horizon 2050, OCÉAN-SENTINELLE utilise des structures d'arbres de décision combinées à des graphes spatiotemporels. Ces simulations doivent intégrer les variables minimales obligatoires :

- Concentration en CO2
- Température de l'eau
- Alcalinité
- Incertitudes explicites

L'utilisation d'une structure de type **"Arbre de Priorité" (Heap)** permet ici de simuler les événements extrêmes en priorité. Dans un scénario de changement climatique, on ne s'intéresse pas seulement à la moyenne, mais aux **"queues de distribution"** (événements de canicule marine ou d'acidification brutale). Le Heap permet de sortir systématiquement les "pires cas" pour aider Alejandro (le décideur) à préparer des dispositifs de soutien financier pour les ostréiculteurs.

---

## Chapitre 7 : Sécurité et Hardening de l'Infrastructure de Données

La gestion des données sensibles (positions de navires, données économiques des parcs) nécessite une sécurité rigoureuse.

- **Secrets Management** : Les clés d'API et accès aux bases de données sont stockés hors du code source dans des fichiers `.env`.
- **Audit et Logs** : Toutes les opérations sur les structures de données critiques sont logguées de manière structurée. L'utilisation d'une file d'attente (Queue) dédiée aux logs garantit que l'audit ne ralentit pas les performances de l'application principale.
- **Règle d'or de la preuve** : Aucun résultat de simulation n'est présenté sans son identifiant de version et sa méthode de calcul, permettant une réplicabilité totale par un tiers.

---

## Chapitre 8 : Architecture Logicielle et Méthodologie "Sandwich"

Le format "Sandwich" imposé pour les rapports (L'Essentiel, Analyse Profonde, Action) trouve un écho dans la stratégie de test logiciel du projet. Le **"Sandwich Testing"** (ou test d'intégration hybride) consiste à tester simultanément les couches hautes (interface utilisateur) et les couches basses (accès aux structures de données de base) pour converger vers la couche intermédiaire (logique métier).

| Phase de Test | Objectif | Correspondance Report |
|--------------|----------|----------------------|
| Top-Down | Vérifier les flux utilisateurs et alertes | L'Essentiel |
| Bottom-Up | Valider l'intégrité des structures (Arrays, Heaps) | Analyse Profonde |
| Middle-Layer | Intégrer la logique ABACODE 2.0 | Action |

Cette approche garantit que les mécanismes au cœur du système (comme la recherche dans une Table de Hachage) sont aussi robustes que l'interface visuelle présentée aux décideurs.

---

## Action

Pour renforcer la résilience de la plateforme GeM OCÉAN-SENTINELLE, les étapes suivantes doivent être initiées immédiatement :

### 1. Génération d'un Tableau de Sensibilité
Simuler l'impact d'une dérive de capteur de pH (±0.1 unités) sur l'indice de mortalité prédit, en utilisant une structure de tableau pour comparer les scénarios.

### 2. Audit de la Table de Hachage AIS
Vérifier le taux de collisions dans l'indexation des MMSI pour le trafic du Golfe de Gascogne et ajuster la fonction de hachage si le temps d'accès dépasse **O(1)** moyen.

### 3. Implémentation du Heap d'Urgence
Développer le module de triage des alertes pour prioriser les données provenant des zones à risque (ex: zones de captage de naissain) lors des épisodes de remontée d'eau profonde (upwelling) acide.

### 4. Test de Performance des Graphes
Évaluer la latence de l'algorithme de recherche de chemin le plus court pour les navires de maintenance en cas de conditions météorologiques dégradées.

### 5. Simulation Monte Carlo
Compte tenu de l'incertitude élevée détectée sur les mesures d'alcalinité totale en Nouvelle-Aquitaine, lancer une simulation de type "Monte Carlo" stockée dans une structure de liste chaînée pour capturer la distribution des risques.

---

## Recommandation Finale

**Voulez-vous que je prépare la simulation pour le scénario d'acidification 2050 (Scénario B) incluant les variables pHT et température?**

Cette simulation utilisera :
- **Tableaux** pour les séries temporelles de pH et température
- **Heap** pour prioriser les événements extrêmes
- **Graphes** pour modéliser la connectivité spatiale des bassins
- **Tables de hachage** pour l'indexation rapide des stations de mesure

---

**Document généré le** : 18 avril 2026  
**Version** : 1.0  
**Conformité** : ABACODE 2.0  
**Auteur** : Équipe Technique Ocean Sentinelle
