/**
 * Ocean Sentinel V3.1 - Dashboard Dynamique
 * Connexion API REST pour affichage données réelles
 */

const API_BASE_URL = 'https://oceansentinelle.fr/api/v1';

// Mapping noms de variables
const VARIABLE_LABELS = {
    'TEMP': 'Température',
    'PSAL': 'Salinité',
    'DOX2': 'Oxygène dissous',
    'PH_TOTAL': 'pH Total'
};

// Seuils critiques SACS
const THRESHOLDS = {
    'DOX2': { operator: '<', value: 150, unit: 'µmol/kg', label: 'HYPOXIE' },
    'PH_TOTAL': { operator: '<', value: 7.80, unit: '', label: 'ACIDIFICATION' },
    'TEMP': { operator: '>', value: 25, unit: '°C', label: 'TEMPÉRATURE ÉLEVÉE' }
};

// Icônes badges de vérité
const STATUS_ICONS = {
    'measured': `<svg class="data-badge__icon" viewBox="0 0 16 16">
        <circle cx="8" cy="8" r="6" fill="currentColor"/>
    </svg>`,
    'inferred': `<svg class="data-badge__icon" viewBox="0 0 16 16">
        <path d="M8 2 A6 6 0 0 1 8 14 Z" fill="currentColor"/>
    </svg>`,
    'simulated': `<svg class="data-badge__icon" viewBox="0 0 16 16">
        <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="2"/>
    </svg>`
};

const STATUS_LABELS = {
    'measured': 'MESURÉ',
    'inferred': 'INFÉRÉ',
    'simulated': 'SIMULÉ'
};

/**
 * Récupère les données d'une station
 */
async function fetchStationData(stationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/station/${stationId}/latest`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Erreur fetch ${stationId}:`, error);
        throw error;
    }
}

/**
 * Formate le timestamp relatif
 */
function formatRelativeTime(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) {
        return `Il y a ${diffMins} minute${diffMins > 1 ? 's' : ''}`;
    } else {
        const diffHours = Math.floor(diffMins / 60);
        return `Il y a ${diffHours} heure${diffHours > 1 ? 's' : ''}`;
    }
}

/**
 * Génère le HTML d'une carte métrique
 */
function renderMetricCard(parameter, stationId) {
    const label = VARIABLE_LABELS[parameter.name] || parameter.name;
    const statusClass = parameter.is_critical ? 'metric-card--critical' : '';
    const badgeClass = `data-badge--${parameter.status}`;
    
    // Seuil
    let thresholdHtml = '';
    if (THRESHOLDS[parameter.name]) {
        const t = THRESHOLDS[parameter.name];
        const icon = parameter.is_critical ? '<span class="metric-card__threshold-icon">⚠️</span>' : '';
        thresholdHtml = `
            <div class="metric-card__threshold">
                ${icon}
                <span>Seuil : ${t.operator} ${t.value}${t.unit}${parameter.is_critical ? ' • ' + t.label : ''}</span>
            </div>
        `;
    }
    
    // Icône source
    const sourceIcon = parameter.status === 'measured' ? '📍' :
                      parameter.status === 'inferred' ? '🛰️' : '🔬';
    
    return `
        <div class="metric-card ${statusClass}">
            <div class="metric-card__header">
                <div class="metric-card__label">${label}</div>
                <div class="data-badge ${badgeClass}">
                    ${STATUS_ICONS[parameter.status]}
                    <span>${STATUS_LABELS[parameter.status]}</span>
                </div>
            </div>
            
            <div class="metric-card__value-container">
                <div class="metric-card__value">
                    ${parameter.value}<span class="metric-card__unit">${parameter.unit}</span>
                </div>
            </div>
            
            ${thresholdHtml}
            
            <div class="metric-card__meta">
                <div class="metric-card__station">
                    <span class="metric-card__station-icon">${sourceIcon}</span>
                    <span>${parameter.source}</span>
                </div>
                <div class="metric-card__timestamp">
                    ${formatRelativeTime(parameter.timestamp)}
                </div>
            </div>
        </div>
    `;
}

/**
 * Génère le HTML d'une alerte critique
 */
function renderCriticalAlert(parameter, stationId) {
    const threshold = THRESHOLDS[parameter.name];
    if (!threshold) return '';
    
    const badgeClass = `data-badge--${parameter.status}`;
    
    return `
        <div class="alert-sacs alert-sacs--critical">
            <div class="alert-sacs__icon">⚠️</div>
            <div class="alert-sacs__content">
                <div class="alert-sacs__header">
                    <span class="alert-sacs__tag">🔴 CRITICAL</span>
                    <h2 class="alert-sacs__title">${threshold.label}</h2>
                </div>
                <div class="alert-sacs__value">
                    ${VARIABLE_LABELS[parameter.name]} ${parameter.value}${parameter.unit} ${threshold.operator} ${threshold.value}${threshold.unit}
                </div>
                <div class="alert-sacs__meta">
                    <div class="data-badge ${badgeClass}">
                        ${STATUS_ICONS[parameter.status]}
                        <span>${STATUS_LABELS[parameter.status]}</span>
                    </div>
                    <span class="alert-sacs__station">${stationId}</span>
                </div>
                <div class="alert-sacs__action">
                    <span class="alert-sacs__action-icon">⚡</span>
                    <span>${parameter.name === 'DOX2' ? 'Risque mortalité huîtres' : 
                           parameter.name === 'PH_TOTAL' ? 'Risque fragilisation coquilles' : 
                           'Surveiller évolution'}</span>
                </div>
            </div>
            <button class="alert-sacs__dismiss" onclick="this.parentElement.remove()" aria-label="Masquer">×</button>
        </div>
    `;
}

/**
 * Charge et affiche les données d'une station
 */
async function loadStation(stationId, gridId) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    
    // Afficher skeleton loading
    grid.innerHTML = `
        <div class="metric-card metric-card--loading" aria-busy="true">
            <div class="metric-card__header">
                <div class="metric-card__label">Chargement...</div>
            </div>
            <div class="metric-card__value-container">
                <div class="metric-card__value">--</div>
            </div>
        </div>
    `.repeat(4);
    
    try {
        const data = await fetchStationData(stationId);
        
        // Générer les cartes
        const cardsHtml = data.parameters
            .sort((a, b) => {
                const order = ['TEMP', 'PSAL', 'DOX2', 'PH_TOTAL'];
                return order.indexOf(a.name) - order.indexOf(b.name);
            })
            .map(param => renderMetricCard(param, stationId))
            .join('');
        
        grid.innerHTML = cardsHtml;
        
        // Générer les alertes critiques
        const criticalParams = data.parameters.filter(p => p.is_critical);
        if (criticalParams.length > 0) {
            const alertsContainer = document.querySelector('.alerts-container');
            if (alertsContainer) {
                const alertsHtml = criticalParams
                    .map(param => renderCriticalAlert(param, stationId))
                    .join('');
                alertsContainer.innerHTML = alertsHtml;
            }
        }
        
    } catch (error) {
        // Afficher erreur
        grid.innerHTML = `
            <div class="metric-card metric-card--error" role="alert">
                <div class="metric-card__error">
                    <div class="metric-card__error-icon">⚠️</div>
                    <p class="metric-card__error-text">
                        Erreur de connexion à la station ${stationId}
                    </p>
                    <button class="metric-card__retry" onclick="loadStation('${stationId}', '${gridId}')">
                        🔄 Réessayer
                    </button>
                </div>
            </div>
        `.repeat(4);
    }
}

/**
 * Initialisation au chargement de la page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Charger les 2 stations
    loadStation('BARAG_PROXY', 'grid-barag');
    loadStation('ARCACHON_EYRAC', 'grid-eyrac');
    
    // Rafraîchir toutes les 5 minutes
    setInterval(() => {
        loadStation('BARAG_PROXY', 'grid-barag');
        loadStation('ARCACHON_EYRAC', 'grid-eyrac');
    }, 5 * 60 * 1000);
});
