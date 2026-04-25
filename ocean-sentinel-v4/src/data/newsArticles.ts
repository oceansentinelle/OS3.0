/**
 * News Articles Data - Actualités Sentinelles
 * 
 * Flux OSINT 2026 pour Ocean Sentinel
 * Système de traçabilité ABACODE 2.0
 */

import type { NewsArticle } from '@/components/news/NewsCard'

export const NEWS_ARTICLES: NewsArticle[] = [
  {
    id: '001',
    title: 'Onde de choc 2027 [Alerte Filière]',
    teaser: 'Le compte à rebours économique de l\'ostréiculture. L\'été 2025 a marqué un tournant critique avec 44% de mortalité sur les naissains.',
    content: 'L\'été 2025 a marqué un tournant critique pour les écosystèmes littoraux avec un taux de mortalité moyen mesuré à 44 % sur les naissains d\'huîtres. Cette perte massive de la ressource juvénile n\'est pas qu\'un simple constat écologique ; elle enclenche un véritable compte à rebours économique pour la filière conchylicole. Le cycle d\'élevage traditionnel d\'une huître nécessitant environ trois ans, ce déficit de 2025 se traduira par une pénurie drastique de produits marchands sur les étals d\'ici 2027. Les données consolidées par les réseaux d\'observation soulignent la vulnérabilité croissante des élevages face aux stress environnementaux estivaux. Pour les entreprises familiales du littoral, l\'enjeu n\'est plus seulement de subir ces épisodes, mais d\'anticiper le choc financier de 2027. L\'urgence d\'une adaptation des pratiques, éclairée par le renseignement environnemental, n\'a jamais été aussi vitale pour garantir la survie économique du secteur.',
    image: '/images/news/naissain-collecteurs.jpg',
    imageAlt: 'Photo macro de collecteurs ostréicoles',
    source: 'CAPENA/Ifremer',
    date: '23 avril 2026',
    status: 'measured',
    certified: true,
    keyData: 'Indicateur : Taux de perte moyen estival des naissains (1ère année) | Valeur : 44% | Méthode : Échantillonnage in situ | Incertitude : Faible (validation croisée)',
  },
  {
    id: '002',
    title: 'pH 8,04 [Alerte Chimique]',
    teaser: 'La chute de la saturation en aragonite menace le recrutement larvaire. La concentration atmosphérique en CO₂ franchit un seuil historique en 2024.',
    content: 'La concentration atmosphérique en dioxyde de carbone franchit un seuil historique en 2024, dépassant officiellement les 420 ppm. Cette hypercapnie force une absorption océanique massive qui altère fondamentalement la thermodynamique de nos eaux côtières. Les relevés confirment une chute critique du pH des eaux de surface à 8,04, contre 8,11 en 1985. En parallèle, le renseignement environnemental pointe une tendance alarmante à la baisse de l\'état de saturation de l\'aragonite (Ω_Arag), avec un déclin mesuré de -0,0100 à -0,0145 par an. Cette dynamique réduit dangereusement la disponibilité des ions carbonates, briques élémentaires indispensables à la biominéralisation.\n\nSi le point de bascule physiologique létal pour la survie des larves d\'huîtres est estimé autour d\'un pH de 7,6, l\'acidification modérée que nous subissons produit déjà des effets sublétaux. Les observations révèlent que les organismes calcifiants forment des coquilles significativement moins épaisses et plus légères, dégradant la résistance biomécanique des jeunes huîtres face aux chocs et aux prédateurs. Cette fragilisation précoce compromet le développement larvaire et souligne l\'urgence d\'une adaptation stratégique de la filière face à une chimie de l\'eau devenue corrosive.',
    image: '/images/news/article-2-ph-acidification.jpg',
    imageAlt: 'Graphique de tendance pH 1985-2024',
    source: 'Copernicus/Ifremer',
    date: '22 avril 2026',
    status: 'measured',
    certified: true,
    keyData: 'Indicateurs : pH surface 8,04 | CO₂ atm. >420 ppm | Tendance Ω_Arag : -0,0100 à -0,0145/an | Méthode : Modélisation biogéochimique + mésocosmes | Incertitude : Faible à Modérée',
  },
  {
    id: '003',
    title: 'Sentinel-2 [Alerte Spatiale]',
    teaser: 'L\'imagerie haute résolution pour traquer le stress biologique. L\'océanographie spatiale (IMINT) révolutionne notre capacité d\'anticipation sur le littoral.',
    content: 'L\'océanographie spatiale (IMINT) révolutionne notre capacité d\'anticipation sur le littoral. Grâce à la constellation européenne Sentinel-2, nous sommes désormais en mesure de cartographier la qualité de l\'eau (turbidité et concentration en chlorophylle-a) sur des zones stratégiques comme le Banc d\'Arguin. Ce suivi s\'opère avec une fréquence de revisite de 5 jours et une résolution spatiale de 10 mètres. Cette capacité d\'observation est un atout majeur du renseignement en sources ouvertes (OSINT) pour surveiller la dynamique très rapide des masses d\'eau côtières.\n\nLe traitement de ces images repose sur l\'algorithme de correction atmosphérique Sen2Cor, qui isole la réflectance marine des perturbations atmosphériques. Couplé à des algorithmes de détection spécifiques (comme le NDCI), ce système atteint une excellente précision d\'estimation, démontrant une corrélation de 0,853 avec les mesures de terrain. En croisant ces cartographies avec nos observatoires locaux, nous pouvons directement corréler le déplacement des panaches sédimentaires ou phytoplanctoniques avec les épisodes de stress biologique subis par les huîtres, offrant un véritable bouclier prédictif à la filière.',
    image: '/images/news/article-3-sentinel2-imint.jpg',
    imageAlt: 'Vue satellite multispectrale du Bassin d\'Arcachon',
    source: 'Copernicus/ESA',
    date: '21 avril 2026',
    status: 'inferred',
    certified: true,
    keyData: 'Indicateurs : Turbidité + Chlorophylle-a | Résolution : 10m | Revisite : 5 jours | Précision : r = 0,853 (R² = 0,728) | Méthode : Télédétection multispectrale (IMINT) + Sen2Cor | Incertitude : Faible à Modérée',
  },
  {
    id: '004',
    title: 'Banc d\'Arguin [Alerte GEOINT]',
    teaser: 'Le Banc d\'Arguin fracturé : Une vigie naturelle en péril. L\'intelligence géospatiale (GEOINT) révèle une érosion fulgurante à l\'entrée du Bassin d\'Arcachon.',
    content: 'L\'intelligence géospatiale (GEOINT) révèle une érosion fulgurante à l\'entrée du Bassin d\'Arcachon. En seulement quatre ans, le Banc d\'Arguin s\'est littéralement disloqué : sa longueur est passée de 7 km en 2022 à environ 4 km en 2026, ce qui représente une réduction de surface de 43 %. Ce rétrécissement spectaculaire, couplé à l\'ouverture de sept brèches, anéantit progressivement le rôle d\'amortisseur de houle de cette barrière sableuse, accroissant significativement les risques de submersion marine pour les communes du littoral interne.\n\nCette fracturation menace un double équilibre. Sur le plan économique, elle compromet directement 50 % de la capacité de production ostréicole d\'Arguin, un secteur hautement stratégique reconnu pour offrir historiquement les meilleurs rendements de croissance du bassin. Sur le plan écologique, la disparition du sable exondé réduit drastiquement l\'habitat des oiseaux nicheurs. Cette dynamique fragilise la reproduction d\'espèces vulnérables comme la sterne caugek, dont le banc d\'Arguin constitue l\'un des deux principaux sites de ponte en France.',
    image: '/images/news/article-4-arguin-geoint.jpg',
    imageAlt: 'Carte thermique d\'érosion du Banc d\'Arguin (Litto3D)',
    source: 'IMINT/CAPENA/DIRM',
    date: '20 avril 2026',
    status: 'measured',
    certified: true,
    keyData: 'Indicateurs : -3 km longueur | 7 brèches | ~43% surface perdue | Méthode : GEOINT (imagerie satellitaire métrique) + observations in situ | Incertitude : Très faible',
  },
  {
    id: '005',
    title: 'Zostères [Alerte Résilience]',
    teaser: 'Le retour des zostères : La biodiversité comme rempart naturel à Salines. Après une régression historique de -84%, les herbiers reprennent vie.',
    content: 'Après avoir subi une régression historique massive atteignant -84 % pour la zostère marine (Zostera marina), les écosystèmes littoraux reprennent des couleurs. Les campagnes de transplantation menées en 2025 sur le secteur de Salines affichent des résultats particulièrement prometteurs avec un taux de survie moyen de 77 %. Cette initiative ciblée a d\'ores et déjà permis de restaurer près de 1 000 m² d\'herbiers. Véritables "poumons verts" de l\'estran, ces angiospermes marines sont des espèces structurantes indispensables pour stabiliser les sédiments et fournir un biotope refuge à de nombreuses espèces.\n\nAu-delà de la restauration de l\'habitat, ces herbiers déploient un bouclier chimique stratégique. Grâce à leur intense activité photosynthétique, les zostères consomment le dioxyde de carbone (CO₂) dissous et régulent localement le pH de l\'eau. Elles créent ainsi une "bulle de résilience" limitant la corrosivité de l\'eau pour les organismes calcifiants environnants, comme les jeunes huîtres. Cette solution fondée sur la nature prouve que la reconquête de la biodiversité est notre meilleur levier d\'adaptation face aux bouleversements climatiques.',
    image: '/images/news/article-5-zosteres-resilience.jpg',
    imageAlt: 'Photo sous-marine d\'herbiers de zostères',
    source: 'SIBA/Ifremer',
    date: '19 avril 2026',
    status: 'measured',
    certified: true,
    keyData: 'Indicateurs : Survie 77% | Surface restaurée ~1 000 m² | Régression Z. marina -84% | Méthode : Cartographie surfacique + échantillonnage in situ | Incertitude : Faible',
  },
]
