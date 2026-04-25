/**
 * Ocean Sentinel V3.2 - Dashboard Dynamique
 * Connexion API REST pour affichage données réelles
 * LOGIQUE BACKEND PRÉSERVÉE - UI REFACTORISÉE
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
    'DOX2': { operator: '<', value: 150, unit: 'µmol/kg', label: 'HYPOXIE', action: 'Risque mortalité huîtres' },
    'PH_TOTAL': { operator: '<', value: 7.80, unit: '', label: 'ACIDIFICATION', action: 'Risque fragilisation coquilles' },
    'TEMP': { operator: '>', value: 25, unit: '°C', label: 'TEMPÉRATURE ÉLEVÉE', action: 'Surveiller évolution' }
};

// Icônes badges de vérité (SVG inline)
const STATUS_ICONS = {
    'measured': '<svg class="badge__icon" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="currentColor"/></svg>',
    'inferred': '<svg class="badge__icon" viewBox="0 0 16 16"><path d="M8 2 A6 6 0 0 1 8 14 Z" fill="currentColor"/></svg>',
    'simulated': '<svg class="badge__icon" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
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
    
    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `Il y a ${diffHours}h`;
    
    return date.toLocaleDateString('fr-FR');
}

/**
 * Génère le HTML d'une carte métrique
 */
function renderMetricCard(parameter) {
    const label = VARIABLE_LABELS[parameter.name] || parameter.name;
    const criticalClass = parameter.is_critical ? 'metric--critical' : '';
    const badgeClass = `badge--${parameter.status}`;
    
    // Seuil
    let thresholdHtml = '';
    if (THRESHOLDS[parameter.name]) {
        const t = THRESHOLDS[parameter.name];
        const icon = parameter.is_critical ? '⚠️ ' : '';
        thresholdHtml = `
            <div class="metric__threshold">
                ${icon}Seuil : ${t.operator} ${t.value}${t.unit}${parameter.is_critical ? ' • ' + t.label : ''}
            </div>
        `;
    }
    
    return `
        <div class="metric ${criticalClass}">
            <div class="metric__header">
                <div class="metric__label">${label}</div>
                <div class="badge ${badgeClass}">
                    ${STATUS_ICONS[parameter.status]}
                    <span>${STATUS_LABELS[parameter.status]}</span>
                </div>
            </div>
            
            <div class="metric__value">
                ${parameter.value}<span class="metric__unit">${parameter.unit}</span>
            </div>
            
            ${thresholdHtml}
            
            <div class="metric__footer">
                <div class="metric__source">${parameter.source}</div>
                <div class="metric__timestamp">${formatRelativeTime(parameter.timestamp)}</div>
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
    
    const badgeClass = `badge--${parameter.status}`;
    
    return `
        <div class="alert">
            <div class="alert__icon">⚠️</div>
            <div class="alert__content">
                <div class="alert__header">
                    <span class="alert__tag">🔴 CRITICAL</span>
                    <h2 class="alert__title">${threshold.label}</h2>
                </div>
                <div class="alert__value">
                    ${VARIABLE_LABELS[parameter.name]} ${parameter.value}${parameter.unit} ${threshold.operator} ${threshold.value}${threshold.unit}
                </div>
                <div class="alert__meta">
                    <div class="badge ${badgeClass}">
                        ${STATUS_ICONS[parameter.status]}
                        <span>${STATUS_LABELS[parameter.status]}</span>
                    </div>
                    <span>Station ${stationId}</span>
                    <span>• ${threshold.action}</span>
                </div>
            </div>
            <button class="alert__dismiss" onclick="this.parentElement.remove()" aria-label="Masquer">×</button>
        </div>
    `;
}

/**
 * Charge et affiche les données d'une station
 */
async function loadStation(stationId, gridId) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    
    try {
        const data = await fetchStationData(stationId);
        
        // Générer les cartes (ordre fixe : TEMP, PSAL, DOX2, PH_TOTAL)
        const order = ['TEMP', 'PSAL', 'DOX2', 'PH_TOTAL'];
        const sortedParams = data.parameters.sort((a, b) => 
            order.indexOf(a.name) - order.indexOf(b.name)
        );
        
        const cardsHtml = sortedParams
            .map(param => renderMetricCard(param))
            .join('');
        
        grid.innerHTML = cardsHtml;
        
        // Générer les alertes critiques
        const criticalParams = data.parameters.filter(p => p.is_critical);
        if (criticalParams.length > 0) {
            const alertsSection = document.getElementById('alerts');
            const alertsContainer = document.getElementById('alertsContainer');
            
            if (alertsSection && alertsContainer) {
                const alertsHtml = criticalParams
                    .map(param => renderCriticalAlert(param, stationId))
                    .join('');
                
                alertsContainer.innerHTML = alertsHtml;
                alertsSection.style.display = 'block';
            }
        }
        
    } catch (error) {
        // Afficher erreur
        grid.innerHTML = `
            <div class="metric metric--error" style="grid-column: 1 / -1;">
                <div class="metric__error">
                    <div class="metric__error-icon">⚠️</div>
                    <p class="metric__error-text">
                        Erreur de connexion à la station ${stationId}
                    </p>
                    <button class="metric__retry" onclick="loadStation('${stationId}', '${gridId}')">
                        🔄 Réessayer
                    </button>
                </div>
            </div>
        `;
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
